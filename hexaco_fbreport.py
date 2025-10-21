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
CSV_PATH = "csv/20251020_nttdatauniv_test.csv"
# CSV_PATH = "csv/20251020_nttdatauniv.csv"
TEMPLATE_PERSON = "tmp/HEXACOfbレポート_本人用_tmp.docx"
TEMPLATE_OFFICE = "tmp/HEXACOfbレポート_事務局用_tmp.docx"
OUT_DIR = "out/"
os.makedirs(OUT_DIR, exist_ok=True)

# 画像サイズ（高さ px）— ここを変えるだけで出力サイズを統一変更できます
RADAR_HEIGHT_PX = 300

# フォント（テンプレ内テキストの標準フォントとして適用を試みます）
FONT_NAME = "MS Gothic"

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
    if x >= 4.0:
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

FORBIDDEN_PAT = re.compile(
    r'(正直・?謙虚さ|HEXACO|H要因|ダーク(?:・?トライアド)|ナルシシズム|マキャベリ[アャ]ニズム|サイコパシー)',
    flags=re.IGNORECASE
)

def sanitize_comment(text: str) -> str:
    # 正規化（全角/半角のゆれを軽減）
    text = unicodedata.normalize("NFKC", text)

    cleaned_lines = []
    for raw_line in text.splitlines():
        line = raw_line.rstrip()

        # 箇条書き（・, -, *, ● など）は「行」ごと判定して消す
        if re.match(r'^\s*[・\-*●◎◼︎▪︎●]', line):
            if FORBIDDEN_PAT.search(line):
                continue
            cleaned_lines.append(line)
            continue

        # 通常文は「文」単位で分割して禁止語を含む文だけ落とす
        sentences = re.split(r'(?<=[。．！？!?」』])\s*', line)  # 句点や閉じ括弧の直後で分割
        kept = [s for s in sentences if s and not FORBIDDEN_PAT.search(s)]

        # 何か残ったら連結、全落ちならこの行はスキップ
        if kept:
            joined = ''.join(kept)

            # 連続句読点や空白の整理（見た目の崩れ防止）
            joined = re.sub(r'[ 　]{2,}', ' ', joined)              # 連続スペース
            joined = re.sub(r'([。．！？!?])\1+', r'\1', joined)    # 句読点の重複
            cleaned_lines.append(joined)

    # 余分な空行を潰して返す
    out = '\n'.join([l for l in cleaned_lines if l.strip()])
    return out.strip()

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

DARK_TRAIT_COLS = ["ダーク傾向", "ナルシシズム", "サイコパシー", "マキャベリズム"]

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

PRIORITY_HEADS_STRENGTH = ["正直・謙虚さ（倫理観）","協調性（利他性・共感性）","誠実性（計画性）","開放性（好奇心）",
                           "高いIQの可能性","いい上司になりやすい可能性","仕事のパフォーマンスが高くなりやすい可能性",
                           "主体的に行動しやすい可能性","ワークエンゲージメントが高くなりやすい可能性","職務の範囲外の仕事を積極的に行う可能性"]

PRIORITY_HEADS_WEAKNESS = ["情動性（不安傾向）","協調性（利他性・共感性）","誠実性（計画性）",
                           "バイアスを持ちやすい可能性","疲れやすい可能性","ネガティブなことを環境のせいにする可能性",
                           "ストレス対処の傾向：問題をとにかく避ける","高いEQの可能性","ポジティブ感情が強い可能性"]

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
MAX_OFFICE_WEAKNESSES = 3

def build_person_prompt(name: str, levels_5: dict, strengths: list, weaknesses: list) -> str:
    lines = []
    lines.append("あなたは産業・組織心理学の専門家です。全角200文字以内で日本語の自然な文を書いてください。")
    # lines.append(f"対象者名: {name}")
    lines.append("HEXACO（本人用5因子）の水準: " + ", ".join([
        f"O={levels_5.get('O','')}",
        f"C={levels_5.get('C','')}",
        f"E={levels_5.get('E','')}",
        f"A={levels_5.get('A','')}",
        f"N={levels_5.get('N','')}",
    ]))

    lines.append("出力方針: O, C, E, A, N のスコアからポジティブに解釈を書いてください。")
    lines.append("開放性は、高いと好奇心が旺盛、低いと既存の手順の最適化に強いこと。")
    lines.append("誠実性は、高いと計画性があり、低いと柔軟性があること。")
    lines.append("外向性は、高いと人前や交流が得意で、低いと一人で集中できること。")
    lines.append("協調性は、高いと思いやりがあり、低いと率直に伝えることができること。")
    lines.append("情動性は、高いと感受性が豊かになり、低いと動じにくいこと。")
    lines.append("禁止: ダーク傾向/ダークトライアド（ナルシシズム、マキャベリズム、サイコパシー）には一切触れないこと。")

    return "\n".join(lines)

def build_office_prompt(name: str, levels_6: dict, strengths: list, weaknesses: list, dark_levels: dict = None) -> str:
    lines = []
    lines.append("あなたは産業・組織心理学の専門家です。全角600文字以内で日本語の自然な文を書いてください。")
    lines.append(f"対象者名: {name}")
    lines.append("HEXACO（事務局用6因子）の水準: " + ", ".join([
        f"H={levels_6.get('H','')}",
        f"E={levels_6.get('E','')}",
        f"X={levels_6.get('X','')}",
        f"A={levels_6.get('A','')}",
        f"C={levels_6.get('C','')}",
        f"O={levels_6.get('O','')}",
    ]))

    if strengths:
        lines.append("強み（high）: " + "、".join(strengths[:MAX_OFFICE_STRENGTHS]))
    if weaknesses:
        lines.append("改善余地（low）: " + "、".join(weaknesses[:MAX_OFFICE_WEAKNESSES]))

    if strengths:
        lines.append("厳守: 肯定的に断定してよいのは high の項目のみ。")
        lines.append("厳守: high に含まれない項目は、強み/得意/高い/～しやすい等と断定しない。")
    else:
        lines.append("厳守: 肯定的な断定表現は禁止。助言は条件付きで簡潔に。")

    lines.append("厳守: high/middle/low は事実。語尾や表現を変えても値は変えない。")
    lines.append("厳守: 例『高いIQの可能性: low』は『…が低い』と明記。逆転表現禁止。")
    lines.append("厳守: low は『〜が低い』または『今後伸ばせる余地がある』と明示し、"
                "高い/得意/～しやすい等へ言い換えない。")

    alerts = []
    if dark_levels:
        for k, v in dark_levels.items():
            sv = str(v).strip().lower()
            if sv in ("middle", "high"):
                alerts.append(f"{k}={v}")

    if alerts:
        lines.append("注意: 以下のダーク傾向でmiddle/highが見られます。")
        lines.append("ダーク傾向: " + "、".join(alerts))
        lines.append("評価文では、烙印的な表現を避け、業務上のリスク（利己的判断、衝動性、規範軽視など）の具体例と、建設的対処（役割設計、フィードバック頻度、意思決定プロセスの透明化等）を簡潔に示してください。")

    lines.append("要件: 人事・教育担当者向けに配置・育成上の示唆を含め、客観的かつ簡潔に、1段落のみ。")

    return "\n".join(lines)

def generate_comment_via_gpt(prompt: str) -> str:
    try:
        resp = client.responses.create(
            # model="gpt-5",
            model="gpt-4o-mini",
            input=prompt,
            temperature=0.1,
            max_output_tokens=512,
        )
        return resp.output_text.strip()
    except Exception:
        return "観察された特性を踏まえ、強みを活かしつつ小さな行動から改善を進めましょう。"

# ------------------ DOCX生成 ------------------

def fill_person_docx(row: pd.Series, radar_buf, out_path: str):
    """本人用（Hなし／O,C,E,A,Nの5因子）"""
    doc = Document(TEMPLATE_PERSON)

    name = str(row.get("Name", "NoName"))
    # 元データの素点（1桁小数）を直接埋め込む
    raw_vals = {
        "O": fmt1(row.get("開放性（好奇心）")),
        "C": fmt1(row.get("誠実性（計画性）")),
        "E": fmt1(row.get("外向性（ポジティブさ）")),
        "A": fmt1(row.get("協調性（利他性・共感性）")),
        "N": fmt1(row.get("情動性（不安傾向）")),
    }
    levels = {
        "O": label_from_score(row.get("開放性（好奇心）")),
        "C": label_from_score(row.get("誠実性（計画性）")),
        "E": label_from_score(row.get("外向性（ポジティブさ）")),
        "A": label_from_score(row.get("協調性（利他性・共感性）")),
        "N": label_from_score(row.get("情動性（不安傾向）")),
    }

    # strengths, weaknesses = collect_level_flags(row, exclude_cols=DARK_TRAIT_COLS)
    strengths, weaknesses = [], []

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

    # コメント
    prompt = build_person_prompt(name, levels, strengths, weaknesses)
    comment = generate_comment_via_gpt(prompt)
    comment = sanitize_comment(comment)
    comment = trim_to_fullwidth_chars(comment, PERSON_COMMENT_LIMIT)
    replace_text_placeholders(doc, {"[comment_about_5_factors]": comment, "[COMMENT]": comment})

    # レーダー画像
    for key in ["[radar_chart_5_factors_height200px]", "[RADAR_5]", "[radar_chart]"]:
        radar_buf.seek(0)
        replace_image_placeholder(doc, key, radar_buf, height_px=RADAR_HEIGHT_PX)

    # フォント適用
    apply_font(doc, FONT_NAME)

    doc.save(out_path)
    convert(out_path, os.path.splitext(out_path)[0] + ".pdf")

def fill_office_docx(row: pd.Series, radar_buf, out_path: str):
    """事務局用（6因子）"""
    doc = Document(TEMPLATE_OFFICE)

    name = str(row.get("Name", "NoName"))
    # 元データの素点（1桁小数）を直接埋め込む
    raw_vals = {
        "H": fmt1(row.get("正直・謙虚さ（倫理観）")),
        "E": fmt1(row.get("情動性（不安傾向）")),
        "X": fmt1(row.get("外向性（ポジティブさ）")),
        "A": fmt1(row.get("協調性（利他性・共感性）")),
        "C": fmt1(row.get("誠実性（計画性）")),
        "O": fmt1(row.get("開放性（好奇心）")),
    }
    levels = {
        "H": label_from_score(row.get("正直・謙虚さ（倫理観）")),
        "E": label_from_score(row.get("情動性（不安傾向）")),
        "X": label_from_score(row.get("外向性（ポジティブさ）")),
        "A": label_from_score(row.get("協調性（利他性・共感性）")),
        "C": label_from_score(row.get("誠実性（計画性）")),
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

    doc.save(out_path)
    convert(out_path, os.path.splitext(out_path)[0] + ".pdf")

# ------------------ メイン ------------------

def main():
    df = pd.read_csv(CSV_PATH, na_values=["NA", "N/A", "na", "NaN", "-", ""], encoding="utf-8")

    # 本人用（5因子）: O, C, E, A, N
    person_cols = ["開放性（好奇心）", "誠実性（計画性）", "外向性（ポジティブさ）", "協調性（利他性・共感性）", "情動性（不安傾向）"]
    # 事務局用（6因子）: H, E, X, A, C, O
    office_cols  = ["正直・謙虚さ（倫理観）", "情動性（不安傾向）", "外向性（ポジティブさ）", "協調性（利他性・共感性）", "誠実性（計画性）", "開放性（好奇心）"]

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

        # DOCX生成
        fill_person_docx(row, buf_p, os.path.join(OUT_DIR, f"{safe_name}_本人用.docx"))
        fill_office_docx(row, buf_o, os.path.join(OUT_DIR, f"{safe_name}_事務局用.docx"))
        print(f"Generated: {os.path.join(OUT_DIR, f'{safe_name}_本人用.docx')}")
        print(f"Generated: {os.path.join(OUT_DIR, f'{safe_name}_事務局用.docx')}")

if __name__ == "__main__":
    main()
