import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
from openai import OpenAI
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# 🔹 APIクライアントを初期化
client = OpenAI(api_key="")  

# 🔹 日本語フォントを登録（MS ゴシック）
font_path = "C:/Windows/Fonts/msgothic.ttc"
pdfmetrics.registerFont(TTFont("MSGothic", font_path))

# 🔹 Matplotlib側のフォント設定（グラフ用）
fontprop = fm.FontProperties(fname=font_path)
plt.rcParams['font.family'] = fontprop.get_name()

# データ読み込み
# df = pd.read_csv("csv/20250417_nttdata_aaa.csv")
df = pd.read_csv("csv/20250417_nttdata_ddd.csv")

# ChatGPTで文章生成
def generate_feedback(row):
    name = row["Name"]
    hexaco_scores = {
        "正直・謙虚さ": row["正直・謙虚さ（倫理観）"],
        "情動性": row["情動性（不安傾向）"],
        "外向性": row["外向性（ポジティブさ）"],
        "協調性": row["協調性（利他性・共感性）"],
        "誠実性": row["誠実性（計画性）"],
        "開放性": row["開放性（好奇心）"],
    }

    strengths = [col for col in df.columns[7:] if row[col] == "high"]
    weaknesses = [col for col in df.columns[7:] if row[col] == "low"]

    prompt = f"""
    あなたは心理学カウンセラーです。
    以下の人のHEXACOスコアと特性評価をもとに、日本語で自然なフィードバックレポートを書いてください。
    - 名前: {name}
    - HEXACOスコア: {hexaco_scores}
    - 強み（high評価）: {strengths}
    - 改善点（low評価）: {weaknesses}
    必ず、強みを称賛し、改善のヒントも提案してください。
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    return response.choices[0].message.content

# レーダーチャート作成
def create_radar_chart(row, filename):
    labels = ["正直・謙虚さ", "情動性", "外向性", "協調性", "誠実性", "開放性"]
    values = [
        row["正直・謙虚さ（倫理観）"],
        row["情動性（不安傾向）"],
        row["外向性（ポジティブさ）"],
        row["協調性（利他性・共感性）"],
        row["誠実性（計画性）"],
        row["開放性（好奇心）"],
    ]
    values += values[:1]
    angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]

    plt.figure(figsize=(4,4))
    ax = plt.subplot(111, polar=True)
    ax.plot(angles, values, "o-", linewidth=2)
    ax.fill(angles, values, alpha=0.25)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=10)
    ax.set_ylim(0, 5)
    plt.title(f"{row['Name']} さんのHEXACOレーダーチャート", size=12, fontproperties=fontprop)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

# PDF作成
def create_pdf(row, feedback_text):
    name = row["Name"]
    chart_file = f"{name}_radar.png"
    create_radar_chart(row, chart_file)

    doc = SimpleDocTemplate(f"{name}_report.pdf")
    styles = getSampleStyleSheet()
    styles["Normal"].fontName = "MSGothic"
    styles["Title"].fontName = "MSGothic"

    content = []
    content.append(Paragraph(f"{name} さんのフィードバックレポート", styles["Title"]))
    content.append(Spacer(1, 20))
    content.append(Image(chart_file, width=300, height=300))
    content.append(Spacer(1, 20))
    content.append(Paragraph(feedback_text, styles["Normal"]))

    doc.build(content)

# 全員分レポート生成
for _, row in df.iterrows():
    feedback_text = generate_feedback(row)
    create_pdf(row, feedback_text)
