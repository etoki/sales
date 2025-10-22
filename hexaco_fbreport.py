# -*- coding: utf-8 -*-
import os
import re
import io
from datetime import datetime, timezone, timedelta
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import unicodedata
from typing import Dict, List, Tuple, Iterable, Optional

from docx import Document
from docx.shared import Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx2pdf import convert

from openai import OpenAI
client = OpenAI(api_key="")


# ------------------ コンフィグ ------------------
# CSV_PATH = "csv/20250417_nttdata_ddd.csv"
CSV_PATH = "csv/20251020_nttdatauniv_test.csv"
# CSV_PATH = "csv/20251020_nttdatauniv.csv"
TEMPLATE_PERSON = "tmp/HEXACOfbレポート_本人用_tmp.docx"
TEMPLATE_OFFICE = "tmp/HEXACOfbレポート_事務局用_tmp.docx"
OUT_DIR = "out/"
OUT_PERSON_WORD = os.path.join(OUT_DIR, "本人用/word")
OUT_PERSON_PDF  = os.path.join(OUT_DIR, "本人用/pdf")
OUT_OFFICE_WORD = os.path.join(OUT_DIR, "事務局用/word")
OUT_OFFICE_PDF  = os.path.join(OUT_DIR, "事務局用/pdf")
for d in [OUT_PERSON_WORD, OUT_PERSON_PDF, OUT_OFFICE_WORD, OUT_OFFICE_PDF]:
    os.makedirs(d, exist_ok=True)

# 画像サイズ（高さ px）— ここを変えるだけで出力サイズを統一変更できます
RADAR_HEIGHT_PX = 300

# フォント（テンプレ内テキストの標準フォントとして適用を試みます）
FONT_NAME = "MS Gothic"

DARK_TRAIT_COLS = ["ダーク傾向", "ナルシシズム", "サイコパシー", "マキャベリズム"]

# ------------------ ユーティリティ ------------------

def jst_today_str():
    jst = timezone(timedelta(hours=9))
    return datetime.now(jst).strftime("%Y/%m/%d")

def sanitize_filename(name: str) -> str:
    safe = re.sub(r'[\\/*?:\"<>|]+', "_", str(name))
    safe = safe.strip()
    return safe or "unknown"

def label_from_score(x: float) -> str:
    if pd.isna(x):
        return "中"
    if x >= 3.8:
        return "高い"
    elif x < 2.5:
        return "低い"
    else:
        return "中"

def fmt1(x) -> str:
    """小数第1位の文字列（元データの小数第1位）"""
    try:
        return f"{float(x):.1f}"
    except Exception:
        return ""

def trim_to_fullwidth_chars(text: str, limit: int) -> str:
    if text is None:
        return ""
    s = text.strip()
    if len(s) <= limit:
        return s
    s = s[:limit]
    last_marume = max(s.rfind("。"), s.rfind("！"), s.rfind("？"))
    if last_marume >= 0:
        s = s[:last_marume+1]
    return s

def collect_level_flags(row, exclude_cols=None, include_middle: bool = False):
    """
    行データから high/low を抽出し、「カラム:値」形式で返す。
    例） strengths = ["主体的に行動しやすい可能性:high", ...]
        weaknesses = ["疲れやすい可能性:low", ...]
    include_middle=True にすると middle も含められる（デフォルトは除外）。
    """
    if exclude_cols is None:
        exclude_cols = []

    strengths, weaknesses = [], []
    for col, val in row.items():
        if col in exclude_cols:
            continue
        if isinstance(val, str):
            sv = val.strip().lower()
            if sv in ("high", "low", "middle"):
                if sv == "high":
                    strengths.append(f"{col}:{sv}")
                elif sv == "low":
                    weaknesses.append(f"{col}:{sv}")
                elif include_middle:
                    # middle もプロンプトに渡したい場合はここで扱う（必要なければ無視される）
                    pass
    return strengths, weaknesses

PRIORITY_HEADS_STRENGTH = ["知能指数（IQ）","ポジティブ感情","モチベーション","主体的行動","人間関係","レジリエンス","リスクに対して冷静"
                           "いい上司になりやすい可能性","仕事のパフォーマンスが高くなりやすい可能性",
                           "ワークエンゲージメントが高くなりやすい可能性","職務の範囲外の仕事を積極的に行う可能性",
                           "ストレス対処の傾向：問題の解決を求める"]

PRIORITY_HEADS_WEAKNESS = ["情動知能（EQ）","バイアス傾向","疲れやすさ","責任転嫁傾向",
                           "社会的手抜き","同調圧力への敏感さ","バーンアウト傾向",
                           "ストレス対処の傾向：問題をとにかく避ける","放任型リーダーシップである可能性"]

def sort_by_priority_strength(items):
    # 「カラム:値」→「カラム」部分だけで優先度リストを引く
    prio = {name: i for i, name in enumerate(PRIORITY_HEADS_STRENGTH)}
    def _key(x: str):
        head = x.split(":", 1)[0] if isinstance(x, str) else x
        return prio.get(head, 10_000)
    return sorted(items, key=_key)


def sort_by_priority_weakness(items):
    # 「カラム:値」→「カラム」部分だけで優先度リストを引く
    prio = {name: i for i, name in enumerate(PRIORITY_HEADS_WEAKNESS)}
    def _key(x: str):
        head = x.split(":", 1)[0] if isinstance(x, str) else x
        return prio.get(head, 10_000)
    return sorted(items, key=_key)

# ------------------ レーダー ------------------

def make_radar_chart_buffer(values, labels, height_px=None, overlay=None, overlay_style=None, fill_alpha=0.25):
    """
    PNGをBytesIOで返す（ファイルは保存しない）
    - values: 主系列（個人）
    - overlay: オーバーレイ系列（例：全体平均）。None可
    - overlay_style: dict（例：{'color':'red','linewidth':2}）
    """
    if height_px is None:
        height_px = RADAR_HEIGHT_PX

    N = len(values)
    angles = np.linspace(0, 2*np.pi, N, endpoint=False).tolist()

    vals_main = list(values) + [values[0]]
    angles2 = angles + [angles[0]]

    fig = plt.figure(figsize=(4, 4))
    ax = fig.add_subplot(111, polar=True)
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_thetagrids(np.degrees(angles), labels)
    ax.set_rlabel_position(0)
    ax.set_ylim(0, 5)

    # main
    ax.plot(angles2, vals_main, linewidth=2)
    ax.fill(angles2, vals_main, alpha=fill_alpha)

    # overlay
    if overlay is not None:
        vals_overlay = list(overlay) + [overlay[0]]
        style = overlay_style or {}
        ax.plot(angles2, vals_overlay, **style)

    plt.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf

# ------------------ テンプレ置換 ------------------

def replace_text_placeholders(doc: Document, mapping: dict):
    def _replace_in_paragraph(paragraph, mapping):
        if not paragraph.text:
            return
        full_text = paragraph.text
        replaced = False
        for key, val in mapping.items():
            if key in full_text:
                full_text = full_text.replace(key, val)
                replaced = True
        if replaced:
            for run in paragraph.runs[::-1]:
                paragraph._p.remove(run._r)
            paragraph.add_run(full_text)

    for p in doc.paragraphs:
        _replace_in_paragraph(p, mapping)

    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    _replace_in_paragraph(p, mapping)

def replace_image_placeholder(doc: Document, placeholder: str, image_source, height_px=None):
    """image_source は BytesIO でもファイルパス文字列でも可"""
    if height_px is None:
        height_px = RADAR_HEIGHT_PX

    targets = []
    for p in doc.paragraphs:
        if placeholder in p.text:
            targets.append(p)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    if placeholder in p.text:
                        targets.append(p)
    for p in targets:
        for run in p.runs[::-1]:
            p._p.remove(run._r)
        height_inch = height_px / 96.0
        run = p.add_run()
        run.add_picture(image_source, height=Inches(height_inch))
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER

# ------------------ フォント適用 ------------------

def apply_font(doc: Document, font_name: str):
    """文書の既定スタイルと段落・表セルのランにフォント名を適用（EastAsiaも設定）"""
    try:
        style = doc.styles["Normal"]
        style.font.name = font_name
        if style._element.rPr is None:
            style._element._new_rPr()
        rFonts = style._element.rPr.rFonts
        rFonts.set(qn("w:eastAsia"), font_name)
    except Exception:
        pass

    def set_run_font(run):
        try:
            run.font.name = font_name
            r = run._r
            r.rPr.rFonts.set(qn("w:eastAsia"), font_name)
        except Exception:
            pass

    for p in doc.paragraphs:
        for run in p.runs:
            set_run_font(run)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    for run in p.runs:
                        set_run_font(run)

# ------------------ コメント生成（APIは空） ------------------

PERSON_COMMENT_LIMIT = 200
OFFICE_COMMENT_LIMIT  = 600

MAX_OFFICE_STRENGTHS = 10
MAX_OFFICE_WEAKNESSES = 10


def build_person_prompt(name: str, scores: dict, levels: dict) -> str:
    """
    name: 受検者名（例: "山田太郎"）
    scores: {"O": 4.3, "C": 3.5, "E": 2.6, "A": 3.7, "N": 3.1}
    levels: {"O": "high"|"middle"|"low", ... for O,C,E,A,N}
    """
    # ここでNG語彙(禁止ワード)は「指示として」渡すだけ。生成後の置換等はしない。
    prompt = f"""
あなたは日本語の文章作成アシスタントです。以下の入力(JSON)に基づき、
受検者本人向けに Big Five（O, C, E, A, N）の特徴コメントを作成してください。

# 目的
- 本人が前向きに理解・活用できる1段落（150〜220字程度、丁寧語）。
- 各特性はその水準（high/middle/low）に対応する面のみを記述し、反対側の特性内容は一切書かない。

# 出力要件
- 日本語、丁寧語。1段落のみ。数値や記号は書かない（スコアの具体数字は書かない）。
- 両面併記は禁止（例：「〜一方で、〜も」は不可）。「バランスが取れている」等の曖昧評価は禁止。
- 最後に1つだけ実践的な行動示唆を入れる（例：「〜を日々メモすると良いでしょう。」）。

# 特性別ガイド（本人用）
- O 開放性:
  - high: 新規性・探究心・幅広い関心・学習意欲・発想の柔軟さ
    - NG語彙: 「既存手順の最適化」「決まった型を守るのが得意」「定型化」「標準化」「保守的」
  - middle: 新しい考えに前向きだが現実的に吟味／必要に応じて取り入れる（両面同時称賛は不可）
  - low: 実務志向・手順安定・既存資源の磨き込み・標準化（「好奇心が非常に強い」等は不可）

- C 勤勉性:
  - high: 計画性・継続力・締切厳守・準備・自己管理
  - middle: 計画と柔軟さを状況で切替（矛盾する二律背反の同時称賛は不可）
  - low: 臨機応変・試行錯誤・スピード重視（緻密な計画で着実は不可）

- E 外向性:
  - high: 社交性・発信力・対人刺激で活性化
  - middle: 必要な場面で発信／集中作業も対人も状況で使い分け（極端表現は不可）
  - low: 集中没頭・聞き手志向・落ち着いた関わり（人前での発信が得意 は不可）

- A 協調性:
  - high: 共感・配慮・信頼形成・協働志向
  - middle: 意見を伝えつつ関係配慮／折衷的
  - low: 率直・交渉・境界設定・合理的主張（過度な迎合は不可）

- N 情動性（逆尺）:
  - high: 感受性・慎重・リスク予期・周囲への気配り（「動じない」は不可）
  - middle: 状況に応じた切替
  - low: 安定・平静・切替の早さ（「繊細で揺れやすい」は不可）

# フォーマット
- 出力は本文のみ。前置き、見出し、箇条書きは禁止。
- 具体的行動示唆を文末1つだけ入れる。

# 入力(JSON)
{{
  "name": "{name}",
  "scores": {scores},
  "levels": {levels}
}}

# 例（出力イメージ：これは生成の参考であり、数値は書かない）
例: 新しい考えを素直に取り入れ、学びを行動に移せる人です。計画を立てて進めつつ、必要な場面ではやり方を見直して改善できます。人前でも個人作業でも集中を保ち、周囲に配慮しながら意見を伝えられます。状況を丁寧に見極める慎重さも活かしています。日々の気づきを短く記録し、次の挑戦にすぐ試すと良いでしょう。
"""
    return prompt.strip()


def build_office_prompt(name: str, levels_6: dict, strengths: list, weaknesses: list, dark_levels: dict = None) -> str:
    # --- ダーク傾向（ある場合のみ軽く注意喚起） ---
    alerts = []
    low_list = []
    if dark_levels:
        for k, v in dark_levels.items():
            sv = str(v).strip().lower()
            if sv in ("middle", "high"):
                alerts.append(f"{k}={v}")
            elif sv == "low":
                low_list.append(k)

    payload = {
        "name": name,
        "hexaco_levels": levels_6,              # 例: {"H":"高い","E":"中",...}
        "strength_hints": strengths,            # high由来のヒント（任意）
        "attention_hints": weaknesses,          # low由来の留意点（任意）
        "dark_trait_levels": dark_levels or {}, # 例: {"ナルシシズム":"low/middle/high", ...}
        "dark_trait_alerts": alerts,            # middle/high のみ
        "dark_trait_low_as_strength": low_list, # low は安定要因（維持推奨、伸長は不可）
    }

    # 例: ["ナルシシズム=high", "サイコパシー=middle"] を一行で提示（無ければ空）
    alerts_line = "、".join(alerts) if alerts else ""

    prompt = f"""
あなたは日本語の文章作成アシスタントです。以下の入力(JSON)を基に、
人事・マネジメント向けの事務局用コメントを**1段落（全角400〜600字）**で作成してください。

# 出力仕様（厳守）
- **1段落のみ／改行なし**。句点「。」で文を区切る。記号や括弧、箇条書き、見出しは使わない。
- **数字・スコア・記号は書かない**（例：% や（）や：や・は使わない）。
- 文字数は**全角換算で400〜600字**。最終工程で**この範囲に厳密調整**すること。

# 構成（文章は一段落で連続して書く）
1) **6因子の結果の要約（およそ100字）**
   - 因子名は次の6つのみを使用可：正直・謙虚さ／情動性／外向性／協調性／勤勉性／開放性
   - 水準語は「高い／中／低い」のみ。**羅列せず**、要点だけ触れる。**数値は出さない**。
   - 表記ゆれ禁止：例「正直謙虚さ」「誠実さ（H）」などに置換しない。

2) **強み（およそ100字）**
   - 入力の strength_hints から**上位優先**で1〜3点選ぶ。
   - **禁止語**：正直・謙虚さ／情動性／外向性／協調性／勤勉性／開放性
     - 上記がヒント内に含まれる場合は除外する。**

3) **弱み・今後の注意（およそ100字）**
   - 入力の attention_hints から**上位優先**で1〜3点選ぶ。
   - **禁止語**：正直・謙虚さ／情動性／外向性／協調性／勤勉性／開放性
     - 含まれる場合は除外する。**

4) **ダーク傾向の扱い（必要時のみ短く）**
   - 「ナルシシズム／マキャベリズム／サイコパシー／ダーク傾向」という語は**本文に出さない**。
   - middle/high がある場合は**中立トーン**で、想定リスク例（利己的判断、衝動性、規範軽視など）を**一例のみ**触れ、
     **対処を1〜2点**だけ示す（役割設計、意思決定の透明化、レビュー頻度設定など）。
   - low は安定要因として触れてもよいが、「伸ばす／増やす」とは書かない（維持の示唆は可）。

# 文体と表現ルール
- **両面併記の乱用禁止**（「一方で〜も」を多用しない）。「バランスが良い」等の曖昧総評は禁止。
- 共感や配慮など**他因子の内容を推測で混同しない**。
- レッテル貼りや断定禁止。丁寧語で簡潔に。

# 自動チェックと調整（生成後に必ず実施）
- 改行があれば**削除**し、全角カウントで**400〜600字に収める**。超過時は末尾から削り、文末は句点で整える。

# 入力(JSON)
{payload}
{alerts_line}
    """
    return prompt

def generate_comment_via_gpt(prompt: str) -> str:
    try:
        resp = client.responses.create(
            model="gpt-4o-mini",
            input=prompt,
            temperature=0.1,
            max_output_tokens=512,
        )
        return resp.output_text.strip()
    except Exception:
        return "観察された特性を踏まえ、強みを活かしつつ小さな行動から改善を進めましょう。"

# ------------------ DOCX生成 ------------------

def fill_person_docx(row: pd.Series, radar_buf, out_docx_path: str, out_pdf_path: str):
    """本人用（Hなし／O,C,E,A,Nの5因子）"""
    doc = Document(TEMPLATE_PERSON)

    name = str(row.get("Name", "NoName"))
    raw_vals = {
        "O": fmt1(row.get("開放性（好奇心）")),
        "C": fmt1(row.get("勤勉性（計画性）")),
        "E": fmt1(row.get("外向性（ポジティブさ）")),
        "A": fmt1(row.get("協調性（利他性・共感性）")),
        "N": fmt1(row.get("情動性（不安傾向）")),
    }
    levels = {
        "O": label_from_score(row.get("開放性（好奇心）")),
        "C": label_from_score(row.get("勤勉性（計画性）")),
        "E": label_from_score(row.get("外向性（ポジティブさ）")),
        "A": label_from_score(row.get("協調性（利他性・共感性）")),
        "N": label_from_score(row.get("情動性（不安傾向）")),
    }
    text_map = {
        "[Name]": name,
        "[YYYY/MM/DD]": jst_today_str(),
        "[reputate_hexaco_O]": levels["O"],
        "[reputate_hexaco_C]": levels["C"],
        "[reputate_hexaco_E]": levels["E"],
        "[reputate_hexaco_A]": levels["A"],
        "[reputate_hexaco_N]": levels["N"],
        "[LEVEL_O]": levels["O"],
        "[LEVEL_C]": levels["C"],
        "[LEVEL_E]": levels["E"],
        "[LEVEL_A]": levels["A"],
        "[LEVEL_N]": levels["N"],
        "[value_hexaco_O]": raw_vals["O"],
        "[value_hexaco_C]": raw_vals["C"],
        "[value_hexaco_E]": raw_vals["E"],
        "[value_hexaco_A]": raw_vals["A"],
        "[value_hexaco_N]": raw_vals["N"],
    }
    replace_text_placeholders(doc, text_map)

    def to_float(v):
        if v is None or v == "":
            return None
        try:
            return float(v)
        except Exception:
            # 余裕があればここでログ出し
            return None

    scores = {k: to_float(v) for k, v in raw_vals.items()}

    name = str(row.get("Name", "")).strip()

    # コメント
    prompt = build_person_prompt(name=name, scores=scores, levels=levels)

    comment = generate_comment_via_gpt(prompt)
    comment = trim_to_fullwidth_chars(comment, PERSON_COMMENT_LIMIT)
    replace_text_placeholders(doc, {"[comment_about_5_factors]": comment, "[COMMENT]": comment})

    # レーダー画像
    for key in ["[radar_chart_5_factors_height200px]", "[RADAR_5]", "[radar_chart]"]:
        radar_buf.seek(0)
        replace_image_placeholder(doc, key, radar_buf, height_px=RADAR_HEIGHT_PX)

    # フォント適用
    apply_font(doc, FONT_NAME)

    doc.save(out_docx_path)
    convert(out_docx_path, out_pdf_path)

def fill_office_docx(row: pd.Series, radar_buf, out_docx_path: str, out_pdf_path: str):
    """事務局用（6因子）"""
    doc = Document(TEMPLATE_OFFICE)

    name = str(row.get("Name", "NoName"))
    # 元データの素点（1桁小数）を直接埋め込む
    raw_vals = {
        "H": fmt1(row.get("正直・謙虚さ（倫理観）")),
        "E": fmt1(row.get("情動性（不安傾向）")),
        "X": fmt1(row.get("外向性（ポジティブさ）")),
        "A": fmt1(row.get("協調性（利他性・共感性）")),
        "C": fmt1(row.get("勤勉性（計画性）")),
        "O": fmt1(row.get("開放性（好奇心）")),
    }
    levels = {
        "H": label_from_score(row.get("正直・謙虚さ（倫理観）")),
        "E": label_from_score(row.get("情動性（不安傾向）")),
        "X": label_from_score(row.get("外向性（ポジティブさ）")),
        "A": label_from_score(row.get("協調性（利他性・共感性）")),
        "C": label_from_score(row.get("勤勉性（計画性）")),
        "O": label_from_score(row.get("開放性（好奇心）")),
    }

    strengths, weaknesses = collect_level_flags(row, exclude_cols=DARK_TRAIT_COLS)

    strengths = sort_by_priority_strength(strengths)
    weaknesses = sort_by_priority_weakness(weaknesses)

    text_map = {
        "[Name]": name,
        "[YYYY/MM/DD]": jst_today_str(),
        "[reputate_hexaco_H]": levels["H"],
        "[reputate_hexaco_E]": levels["E"],
        "[reputate_hexaco_X]": levels["X"],
        "[reputate_hexaco_A]": levels["A"],
        "[reputate_hexaco_C]": levels["C"],
        "[reputate_hexaco_O]": levels["O"],
        "[LEVEL_H]": levels["H"],
        "[LEVEL_E]": levels["E"],
        "[LEVEL_X]": levels["X"],
        "[LEVEL_A]": levels["A"],
        "[LEVEL_C]": levels["C"],
        "[LEVEL_O]": levels["O"],
        "[value_hexaco_H]": raw_vals["H"],
        "[value_hexaco_E]": raw_vals["E"],
        "[value_hexaco_X]": raw_vals["X"],
        "[value_hexaco_A]": raw_vals["A"],
        "[value_hexaco_C]": raw_vals["C"],
        "[value_hexaco_O]": raw_vals["O"],
    }
    replace_text_placeholders(doc, text_map)

    dark_levels = {}
    for col in DARK_TRAIT_COLS:
        if col in row.index:
            dark_levels[col] = row[col]

    # コメント
    prompt = build_office_prompt(name, levels, strengths, weaknesses, dark_levels=dark_levels)
    comment = generate_comment_via_gpt(prompt)
    comment = trim_to_fullwidth_chars(comment, OFFICE_COMMENT_LIMIT)
    replace_text_placeholders(doc, {"[comment_about_6_factors_and_darktrait]": comment, "[COMMENT]": comment})

    # レーダー画像（事務局用は main 内で平均オーバーレイ済みのバッファを受け取る）
    for key in ["[radar_chart_6_factors_height200px]", "[RADAR_6]", "[radar_chart]"]:
        radar_buf.seek(0)
        replace_image_placeholder(doc, key, radar_buf, height_px=RADAR_HEIGHT_PX)

    # フォント適用
    apply_font(doc, FONT_NAME)

    doc.save(out_docx_path)
    convert(out_docx_path, out_pdf_path)

# ------------------ メイン ------------------

def main():
    df = pd.read_csv(CSV_PATH, na_values=["NA", "N/A", "na", "NaN", "-", ""], encoding="utf-8")

    DROP_COLS_EXACT = [
        "価値観の傾向：人や資源を管理し、お金を求める",
        "価値観の傾向：社会的に認められた成功を求める",
        "価値観の傾向：快楽を求める",
        "価値観の傾向：刺激的な経験を求める",
        "価値観の傾向：思考と行動の独立性を求める",
        "価値観の傾向：平等や社会的正義や環境保護を求める",
        "価値観の傾向：周りの人々の繁栄や幸福を求める",
        "価値観の傾向：他人の期待に応えるために自らの衝動をコントロールする",
        "価値観の傾向：伝統を守る",
        "価値観の傾向：自分・家族・国家の安全や安心を求める"
    ]
    exact_hits = [c for c in DROP_COLS_EXACT if c in df.columns]

    cols_to_drop = sorted(set(exact_hits))
    if cols_to_drop:
        df = df.drop(columns=cols_to_drop, errors="ignore")

    # 本人用（5因子）: O, C, E, A, N
    person_cols = ["開放性（好奇心）", "勤勉性（計画性）", "外向性（ポジティブさ）", "協調性（利他性・共感性）", "情動性（不安傾向）"]
    # 事務局用（6因子）: H, E, X, A, C, O
    office_cols  = ["正直・謙虚さ（倫理観）", "情動性（不安傾向）", "外向性（ポジティブさ）", "協調性（利他性・共感性）", "勤勉性（計画性）", "開放性（好奇心）"]

    # 数値化＆クリップ
    for c in set(person_cols + office_cols):
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").clip(lower=0, upper=5)

    # 事務局用の全体平均（6因子の順で）
    avg_series = df[office_cols].mean(numeric_only=True)
    avg_vals = avg_series.fillna(avg_series.mean() if not np.isnan(avg_series.mean()) else 0).tolist()

    for idx, row in df.iterrows():
        name = str(row.get("Name", f"row{idx+1}"))
        safe_name = sanitize_filename(name)

        # レーダー（本人用・5因子）
        vals_p = [row.get(c, np.nan) for c in person_cols]
        s_p = pd.Series(vals_p, dtype="float64")
        filled_p = s_p.fillna(s_p.mean() if not np.isnan(s_p.mean()) else 0).tolist()
        buf_p = make_radar_chart_buffer(
            filled_p,
            ["O", "C", "E", "A", "N"],
            height_px=RADAR_HEIGHT_PX
        )

        # レーダー（事務局用・6因子） — 全体平均を赤線でオーバーレイ
        vals_o = [row.get(c, np.nan) for c in office_cols]
        s_o = pd.Series(vals_o, dtype="float64")
        filled_o = s_o.fillna(s_o.mean() if not np.isnan(s_o.mean()) else 0).tolist()
        buf_o = make_radar_chart_buffer(
            filled_o,
            ["H", "E", "X", "A", "C", "O"],
            height_px=RADAR_HEIGHT_PX,
            overlay=avg_vals,
            overlay_style={"color": "red", "linewidth": 2},
            fill_alpha=0.20,
        )

        # ---- パスを作る（4フォルダに振り分ける）----
        person_docx = os.path.join(OUT_PERSON_WORD, f"{safe_name}_本人用.docx")
        person_pdf  = os.path.join(OUT_PERSON_PDF,  f"{safe_name}_本人用.pdf")
        office_docx = os.path.join(OUT_OFFICE_WORD, f"{safe_name}_事務局用.docx")
        office_pdf  = os.path.join(OUT_OFFICE_PDF,  f"{safe_name}_事務局用.pdf")

        # ---- 出力 ----
        # fill_person_docx(row, buf_p, person_docx, person_pdf)
        fill_office_docx(row, buf_o, office_docx, office_pdf)

        print(f"Generated: {person_docx}")
        print(f"Generated: {person_pdf}")
        print(f"Generated: {office_docx}")
        print(f"Generated: {office_pdf}")

if __name__ == "__main__":
    main()
