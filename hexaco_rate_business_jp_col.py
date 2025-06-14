import pandas as pd

# data.csvを読み込む
file_path = 'csv/data.csv'
data = pd.read_csv(file_path)

# 閾値の設定
l = 0.45
h = 0.7


# HEXACOスコアから指標を計算する関数
def calculate_indicators(row):
    # 非認知能力の計算
    dark_trend = (0.6 if row['Honesty-Humility'] <= 2.5 else 0) \
                + (0.4 if row['Agreeableness'] <= 2.5 else 0)
    narcissism = (0.3 if row['Honesty-Humility'] <= 2.5 else 0) \
                + (0.3 if row['Agreeableness'] <= 3.0 else 0) \
                + (0.2 if row['Extraversion'] >= 4.0 else 0) \
                + (0.2 if row['Openness'] >= 4.0 else 0)
    psychopathy = (0.3 if row['Honesty-Humility'] <= 2.5 else 0) \
                + (0.3 if row['Agreeableness'] <= 2.5 else 0) \
                + (0.2 if row['Emotionality'] <= 2.5 else 0) \
                + (0.1 if row['Extraversion'] <= 3.0 else 0) \
                + (0.1 if row['Conscientiousness'] <= 3.0 else 0)
    machiavellianism = (0.3 if row['Honesty-Humility'] <= 2.5 else 0) \
                    + (0.3 if row['Agreeableness'] <= 2.5 else 0) \
                    + (0.2 if row['Emotionality'] <= 3.0 else 0) \
                    + (0.1 if row['Extraversion'] <= 3.0 else 0) \
                    + (0.1 if row['Openness'] >= 3.0 else 0)
    highIQ = (0.7 if row['Openness'] >= 4 else 0) \
            + (0.3 if row['Emotionality'] <= 3 else 0)
    highEQ = (0.25 if row['Extraversion'] >= 4 else 0) \
            + (0.25 if row['Conscientiousness'] >= 4 else 0) \
            + (0.25 if row['Agreeableness'] >= 4 else 0) \
            + (0.25 if row['Openness'] >= 4 else 0)
    critical_thinking = (0.6 if row['Openness'] >= 4 else 0) \
                        + (0.2 if row['Agreeableness'] >= 4 else 0) \
                        + (0.2 if row['Emotionality'] <= 3 else 0)
    effort = 1 if row['Conscientiousness'] >= 4 else 0.5 if row['Conscientiousness'] >= 3.5 else 0
    high_motivation = (0.3 if row['Honesty-Humility'] >= 4 else 0) \
                    + (0.1 if row['Emotionality'] >= 4 else 0) \
                    + (0.1 if row['Extraversion'] >= 4 else 0) \
                    + (0.3 if row['Conscientiousness'] >= 4 else 0) \
                    + (0.2 if row['Openness'] >= 4 else 0)
    sdt_autonomy = (0.33 if row['Extraversion'] >= 4 else 0) \
                + (0.33 if row['Agreeableness'] >= 4 else 0) \
                + (0.34 if row['Emotionality'] <= 3 else 0)
    sdt_competent = (0.33 if row['Extraversion'] >= 4 else 0) \
                    + (0.33 if row['Conscientiousness'] >= 4 else 0) \
                    + (0.34 if row['Emotionality'] <= 3 else 0)
    sdt_relation = (0.5 if row['Extraversion'] >= 4 else 0) \
                + (0.5 if row['Emotionality'] <= 3 else 0)
    listening_to_others = 1 if row['Extraversion'] <= 3 else 0.5 if row['Extraversion'] <= 3.5 else 0
    adapting_to_change  = 1 if row['Extraversion'] <= 3 else 0.5 if row['Extraversion'] <= 3.5 else 0
    # listening_to_others = 1 if row['Extraversion'] <= 3 else 0
    # adapting_to_change  = 1 if row['Extraversion'] <= 3 else 0
    feel_happiness = (0.33 if row['Extraversion'] >= 4 else 0) \
                    + (0.33 if row['Agreeableness'] >= 4 else 0) \
                    + (0.34 if row['Emotionality'] <= 3 else 0)
    feel_lucky = (0.33 if row['Extraversion'] >= 4 else 0) \
                + (0.33 if row['Openness'] >= 4 else 0) \
                + (0.34 if row['Emotionality'] <= 3 else 0)
    high_self_efficacy = (0.33 if row['Extraversion'] >= 4 else 0) \
                        + (0.33 if row['Conscientiousness'] >= 4 else 0) \
                        + (0.34 if row['Emotionality'] <= 3 else 0)
    positive_thinking = (0.35 if row['Extraversion'] >= 4 else 0) \
                        + (0.1 if row['Openness'] >= 4 else 0) \
                        + (0.1 if row['Agreeableness'] >= 4 else 0) \
                        + (0.35 if row['Conscientiousness'] >= 4 else 0) \
                        + (0.1 if row['Emotionality'] <= 3 else 0)
    resilience = (0.5 if row['Honesty-Humility'] >= 4 else 0) \
                + (0.5 if row['Extraversion'] >= 4 else 0)
    coping_problem_solving = (0.25 if row['Extraversion'] >= 4 else 0) \
                            + (0.25 if row['Conscientiousness'] >= 4 else 0) \
                            + (0.25 if row['Emotionality'] <= 3 else 0) \
                            + (0.25 if row['Openness'] >= 4 else 0)
    coping_emotional_support = (0.33 if row['Extraversion'] >= 4 else 0) \
                            + (0.33 if row['Agreeableness'] >= 4 else 0) \
                            + (0.34 if row['Emotionality'] >= 4 else 0)
    coping_recreation = (0.33 if row['Extraversion'] >= 4 else 0) \
                    + (0.33 if row['Conscientiousness'] >= 4 else 0) \
                    + (0.34 if row['Emotionality'] >= 4 else 0)
    coping_cognitive_restructuring = (0.25 if row['Extraversion'] >= 4 else 0) \
                                + (0.25 if row['Conscientiousness'] >= 4 else 0) \
                                + (0.25 if row['Emotionality'] <= 3 else 0) \
                                + (0.25 if row['Agreeableness'] >= 4 else 0)
    coping_acceptance = (0.5 if row['Agreeableness'] >= 4 else 0) \
                        + (0.5 if row['Emotionality'] <= 3 else 0)
    coping_avoidance = (0.5 if row['Conscientiousness'] <= 3 else 0) \
                    + (0.5 if row['Emotionality'] >= 4 else 0)
    coping_denial = (0.33 if row['Conscientiousness'] <= 3 else 0) \
                + (0.33 if row['Agreeableness'] <= 3 else 0) \
                + (0.34 if row['Emotionality'] >= 4 else 0)
    coping_wishful_thinking = (0.5 if row['Openness'] >= 4 else 0) \
                            + (0.5 if row['Emotionality'] >= 4 else 0)
    coping_withdrawal = (0.5 if row['Openness'] >= 4 else 0) \
                    + (0.5 if row['Emotionality'] >= 4 else 0)
    coping_negative_emotion = (0.33 if row['Conscientiousness'] <= 3 else 0) \
                            + (0.33 if row['Agreeableness'] <= 3 else 0) \
                            + (0.34 if row['Emotionality'] >= 4 else 0)
    coping_substance_use = (0.33 if row['Conscientiousness'] <= 4 else 0) \
                        + (0.33 if row['Agreeableness'] <= 4 else 0) \
                        + (0.34 if row['Emotionality'] >= 4 else 0)
    coping_religious = (0.5 if row['Agreeableness'] >= 4 else 0) \
                    + (0.5 if row['Openness'] <= 3 else 0)

    risk_humble_calm = 1 if row['Conscientiousness'] >= 4 else 0.5 if row['Conscientiousness'] >= 3.5 else 0
    # risk_humble_calm = 1 if row['Conscientiousness'] >= 4 else 0
    risk_low_regret = 1 if row['Openness'] >= 4 else 0.5 if row['Openness'] >= 3.5 else 0
    # risk_low_regret = 1 if row['Openness'] >= 4 else 0
    risk_challenge = (0.6 if row['Openness'] >= 4 else 0) \
                    + (0.4 if row['Conscientiousness'] <= 3 else 0)
    risk_strong_bias = 1 if row['Emotionality'] >= 4 else 0.5 if row['Emotionality'] >= 3.5 else 0
    # risk_strong_bias = 1 if row['Emotionality'] >= 4 else 0
    
    # 価値観・認識
    spirituality = (0.6 if row['Openness'] >= 4 else 0) \
                 + (0.4 if row['Agreeableness'] >= 4 else 0)
    like_power = (0.5 if row['Extraversion'] >= 4 else 0) \
               + (0.5 if row['Agreeableness'] <= 3 else 0)
    like_achievement = (0.5 if row['Extraversion'] >= 4 else 0) \
                  + (0.5 if row['Agreeableness'] <= 3 else 0)
    like_pleasure = (0.5 if row['Extraversion'] >= 4 else 0) \
                  + (0.5 if row['Conscientiousness'] <= 3 else 0)
    like_exciting = (0.5 if row['Extraversion'] >= 4 else 0) \
                  + (0.5 if row['Openness'] >= 4 else 0)
    like_independence = (0.5 if row['Extraversion'] >= 4 else 0) \
                      + (0.5 if row['Openness'] >= 4 else 0)
    like_universal = (0.5 if row['Openness'] >= 4 else 0) \
                    + (0.5 if row['Agreeableness'] >= 4 else 0)
    like_philanthropy = 1 if row['Agreeableness'] >= 4 else 0.5 if row['Agreeableness'] >= 3.5 else 0
    # like_philanthropy = 1 if row['Agreeableness'] >= 4 else 0
    like_harmony = (0.33 if row['Openness'] <= 3 else 0) \
                + (0.33 if row['Agreeableness'] >= 4 else 0) \
                + (0.34 if row['Conscientiousness'] >= 4 else 0)
    like_tradition = (0.33 if row['Extraversion'] <= 3 else 0) \
                    + (0.33 if row['Openness'] <= 3 else 0) \
                    + (0.34 if row['Agreeableness'] >= 4 else 0)
    like_safety = (0.5 if row['Openness'] <= 3 else 0) \
                + (0.5 if row['Conscientiousness'] >= 4 else 0)
    politics_left = 1 if row['Openness'] >= 4 else 0.5 if row['Openness'] >= 3.5 else 0
    # politics_left = 1 if row['Openness'] >= 4 else 0
    politics_right = (0.33 if row['Honesty-Humility'] <= 3 else 0) \
                    + (0.33 if row['Openness'] <= 3 else 0) \
                    + (0.34 if row['Conscientiousness'] >= 4 else 0)
    proenvironmental_attitudes = (0.5 if row['Honesty-Humility'] >= 4 else 0) \
                                + (0.5 if row['Openness'] >= 4 else 0)
    prejudice_rwa = (0.5 if row['Conscientiousness'] >= 4 else 0) \
                    + (0.5 if row['Openness'] <= 3 else 0)
    prejudice_sdo = 1 if row['Agreeableness'] <= 2.5 else 0.5 if row['Agreeableness'] <= 3.0 else 0
    # prejudice_sdo = 1 if row['Agreeableness'] <= 3 else 0
    beliefin_unjust_world = (0.167 if row['Honesty-Humility'] <= 3 else 0) \
                          + (0.167 if row['Emotionality'] >= 4 else 0) \
                          + (0.167 if row['Extraversion'] <= 3 else 0) \
                          + (0.167 if row['Agreeableness'] <= 3 else 0) \
                          + (0.166 if row['Conscientiousness'] <= 3 else 0) \
                          + (0.166 if row['Openness'] <= 3 else 0)
    compatibility_1 = 1 if row['Honesty-Humility'] >= 3 and row['Openness'] >= 3 else 0
    compatibility_2 = 1 if row['Honesty-Humility'] < 3 and row['Openness'] >= 3 else 0
    compatibility_3 = 1 if row['Honesty-Humility'] >= 3 and row['Openness'] < 3 else 0
    compatibility_4 = 1 if row['Honesty-Humility'] < 3 and row['Openness'] < 3 else 0
    social_loafing = 1 if row['Conscientiousness'] <= 2.5 else 0.5 if row['Conscientiousness'] <= 3.0 else 0
    # social_loafing = 1 if row['Conscientiousness'] <= 3 else 0
    feel_peer_pressure = (0.25 if row['Emotionality'] >= 4 else 0) \
                        + (0.25 if row['Extraversion'] >= 4 else 0) \
                        + (0.25 if row['Agreeableness'] >= 4 else 0) \
                        + (0.25 if row['Conscientiousness'] >= 4 else 0)

    # 学力・仕事
    high_academic_performance = (0.33 if row['Agreeableness'] >= 4 else 0) \
                            + (0.33 if row['Openness'] >= 4 else 0) \
                            + (0.34 if row['Conscientiousness'] >= 4 else 0)
    high_online_learning = (0.5 if row['Openness'] >= 4 else 0) \
                        + (0.5 if row['Conscientiousness'] >= 4 else 0)
    high_income = (0.2 if row['Extraversion'] >= 4 else 0) \
                + (0.2 if row['Conscientiousness'] >= 4 else 0) \
                + (0.2 if row['Openness'] >= 4 else 0) \
                + (0.2 if row['Emotionality'] <= 3 else 0) \
                + (0.2 if row['Agreeableness'] <= 3 else 0)
    high_job_performance = (0.5 if row['Conscientiousness'] >= 4 else 0) \
                        + (0.5 if row['Emotionality'] <= 3 else 0)
    career_success = (0.33 if row['Extraversion'] >= 4 else 0) \
                    + (0.33 if row['Conscientiousness'] >= 4 else 0) \
                    + (0.34 if row['Emotionality'] <= 3 else 0)
    adapting_to_complex_work = 1 if row['Extraversion'] <= 3 else 0.5 if row['Extraversion'] <= 3.5 else 0
    # adapting_to_complex_work = 1 if row['Extraversion'] <= 3 else 0
    good_team = (0.5 if row['Conscientiousness'] >= 4 else 0) \
                + (0.5 if row['Agreeableness'] >= 4 else 0)
    resignation = (0.33 if row['Extraversion'] >= 4 else 0) \
                + (0.33 if row['Openness'] >= 4 else 0) \
                + (0.34 if row['Agreeableness'] <= 3 else 0)
    tired = (0.33 if row['Extraversion'] <= 3 else 0) \
            + (0.33 if row['Emotionality'] >= 4 else 0) \
            + (0.34 if row['Conscientiousness'] <= 3 else 0)
    burn_out = (0.25 if row['Extraversion'] <= 3 else 0) \
                + (0.25 if row['Emotionality'] >= 4 else 0) \
                + (0.25 if row['Conscientiousness'] <= 3 else 0) \
                + (0.25 if row['Agreeableness'] <= 3 else 0)
    remote_work = (0.5 if row['Emotionality'] <= 3 else 0) \
                + (0.5 if row['Conscientiousness'] >= 4 else 0)
    engagement = (0.25 if row['Extraversion'] >= 4 else 0) \
                + (0.25 if row['Conscientiousness'] >= 4 else 0) \
                + (0.25 if row['Openness'] >= 4 else 0) \
                + (0.25 if row['Emotionality'] <= 3 else 0)
    organizational_commitment = (0.25 if row['Extraversion'] >= 4 else 0) \
                            + (0.25 if row['Conscientiousness'] >= 4 else 0) \
                            + (0.25 if row['Openness'] >= 4 else 0) \
                            + (0.25 if row['Emotionality'] <= 3 else 0)
    ocb = (0.25 if row['Extraversion'] >= 4 else 0) \
        + (0.25 if row['Conscientiousness'] >= 4 else 0) \
        + (0.25 if row['Openness'] >= 4 else 0) \
        + (0.25 if row['Honesty-Humility'] >= 4 else 0)
    ocb_individual = (0.5 if row['Conscientiousness'] >= 4 else 0) \
                    + (0.5 if row['Agreeableness'] >= 4 else 0)
    ocb_organization = (0.5 if row['Conscientiousness'] >= 4 else 0) \
                    + (0.5 if row['Openness'] >= 4 else 0)
    ocb_change = (0.5 if row['Extraversion'] >= 4 else 0) \
                + (0.5 if row['Openness'] >= 4 else 0)
    interpersonal_task = (0.33 if row['Extraversion'] >= 4 else 0) \
                    + (0.33 if row['Conscientiousness'] >= 4 else 0) \
                    + (0.34 if row['Openness'] >= 4 else 0)
    learning_goal_orientation = (0.33 if row['Extraversion'] >= 4 else 0) \
                            + (0.33 if row['Conscientiousness'] >= 4 else 0) \
                            + (0.34 if row['Openness'] >= 4 else 0)
    surface_learning = (0.5 if row['Conscientiousness'] >= 4 else 0) \
                    + (0.5 if row['Agreeableness'] >= 4 else 0)
    effective_coaching = (0.25 if row['Extraversion'] >= 4 else 0) \
                        + (0.25 if row['Conscientiousness'] >= 4 else 0) \
                        + (0.25 if row['Openness'] >= 4 else 0) \
                        + (0.25 if row['Emotionality'] <= 3 else 0)
    job_crafting = (0.25 if row['Extraversion'] >= 4 else 0) \
                + (0.25 if row['Conscientiousness'] >= 4 else 0) \
                + (0.25 if row['Openness'] >= 4 else 0) \
                + (0.25 if row['Agreeableness'] >= 4 else 0)
    entrepreneur_innovative_mind = (0.25 if row['Extraversion'] >= 4 else 0) \
                            + (0.25 if row['Conscientiousness'] >= 4 else 0) \
                            + (0.25 if row['Openness'] >= 4 else 0) \
                            + (0.25 if row['Emotionality'] <= 3 else 0)
    supportive_boss = (0.25 if row['Extraversion'] >= 4 else 0) \
                    + (0.25 if row['Conscientiousness'] >= 4 else 0) \
                    + (0.25 if row['Openness'] >= 4 else 0) \
                    + (0.25 if row['Agreeableness'] >= 4 else 0)
    leadership_transformational = (0.167 if row['Extraversion'] >= 4 else 0) \
                            + (0.167 if row['Conscientiousness'] >= 4 else 0) \
                            + (0.167 if row['Openness'] >= 4 else 0) \
                            + (0.167 if row['Agreeableness'] >= 4 else 0) \
                            + (0.166 if row['Honesty-Humility'] >= 4 else 0) \
                            + (0.166 if row['Emotionality'] <= 3 else 0)
    leadership_laissez_faire = (0.33 if row['Extraversion'] <= 3 else 0) \
                            + (0.33 if row['Conscientiousness'] <= 3 else 0) \
                            + (0.34 if row['Agreeableness'] >= 3 else 0)
    leadership_destructive = (0.25 if row['Honesty-Humility'] <= 3 else 0) \
                            + (0.25 if row['Agreeableness'] <= 3 else 0) \
                            + (0.25 if row['Conscientiousness'] <= 3 else 0) \
                            + (0.25 if row['Emotionality'] >= 4 else 0)
    followership_transformational = (0.33 if row['Honesty-Humility'] <= 3 else 0) \
                                + (0.33 if row['Extraversion'] >= 4 else 0) \
                                + (0.34 if row['Openness'] >= 4 else 0)
    followership_relational = 1 if row['Emotionality'] >= 4 else 0.5 if row['Emotionality'] >= 3.5 else 0
    # followership_relational = 1 if row['Emotionality'] >= 4 else 0
    followership_realistic = (0.5 if row['Emotionality'] >= 4 else 0) \
                            + (0.5 if row['Openness'] <= 3 else 0)

    # それぞれの指標をlow, middle, highに分類する
    def classify(value):
        if value < l:
            return 'low'
        elif value >= h:
            return 'high'
        else:
            return 'middle'
    
    return pd.Series({
        'ダーク傾向': classify(dark_trend),
        'ナルシシズム': classify(narcissism),
        'サイコパシー': classify(psychopathy),
        'マキャベリズム': classify(machiavellianism),
        '高いIQの可能性あり': classify(highIQ),
        '高いEQの可能性あり': classify(highEQ),
        '批判的思考ができる': classify(critical_thinking),
        '努力家に多い': classify(effort),
        'モチベーションが高い': classify(high_motivation),
        '主体的に行動しやすい': classify(sdt_autonomy),
        '自信を持ちやすい': classify(sdt_competent),
        '周囲といい関係を持ちやすい': classify(sdt_relation),
        '傾聴できる': classify(listening_to_others),
        '変化へ適応できる': classify(adapting_to_change),
        '幸せを感じやすい': classify(feel_happiness),
        '運がいいと感じやすい': classify(feel_lucky),
        '自己効力感が高い': classify(high_self_efficacy),
        'ポジティブ感情が強い': classify(positive_thinking),
        'レジリエンスがある': classify(resilience),
        'ストレス対処：問題の解決を求める': classify(coping_problem_solving),
        'ストレス対処：慰めや共感を他者に求める': classify(coping_emotional_support),
        'ストレス対処：気晴らしをする': classify(coping_recreation),
        'ストレス対処：状況をより肯定的に捉え直す': classify(coping_cognitive_restructuring),
        'ストレス対処：状況を受け入れる': classify(coping_acceptance),
        'ストレス対処：問題をとにかく避ける': classify(coping_avoidance),
        'ストレス対処：問題を認めない、感情を隠す': classify(coping_denial),
        'ストレス対処：魔法のような救済を望む': classify(coping_wishful_thinking),
        'ストレス対処：引きこもる': classify(coping_withdrawal),
        'ストレス対処：泣く、物をなげる、自己非難': classify(coping_negative_emotion),
        'ストレス対処：アルコールやニコチンなどに頼る': classify(coping_substance_use),
        'ストレス対処：宗教的活動に参加する': classify(coping_religious),
        'リスクに対して謙虚・冷静': classify(risk_humble_calm),
        '失敗しても後悔しづらい': classify(risk_low_regret),
        'リスクがあっても挑戦する': classify(risk_challenge),
        'バイアスを持ちやすい': classify(risk_strong_bias),
        '人生の意味や超越的な物事を求める': classify(spirituality),
        '価値観：人や資源を管理し、お金を求める': classify(like_power),
        '価値観：社会的に認められた成功を求める': classify(like_achievement),
        '価値観：快楽を求める': classify(like_pleasure),
        '価値観：刺激的な経験を求める': classify(like_exciting),
        '価値観：思考と行動の独立性を求める': classify(like_independence),
        '価値観：平等、社会的正義、環境保護を求める': classify(like_universal),
        '価値観：周りの人々の繁栄や幸福を求める': classify(like_philanthropy),
        '価値観：他人の期待に応えるために自らの衝動をコントロールする': classify(like_harmony),
        '価値観：伝統を守る': classify(like_tradition),
        '価値観：自分、家族、国家の安全や安心を求める': classify(like_safety),
        '政治は左派政党を好む': classify(politics_left),
        '政治は右派政党を好む': classify(politics_right),
        '環境保護に興味がある': classify(proenvironmental_attitudes),
        '右翼的権威主義：規範から外れた人を攻撃しやすい': classify(prejudice_rwa),
        '社会的支配志向性：差別や偏見を持ちやすい': classify(prejudice_sdo),
        'ネガティブなことを環境のせいにしがち': classify(beliefin_unjust_world),
        '相性がいい人：開放性と正直謙虚さが高い': classify(compatibility_1),
        '相性がいい人：開放性が高く、正直謙虚さが低い': classify(compatibility_2),
        '相性がいい人：開放性が低く、正直謙虚さが高い': classify(compatibility_3),
        '相性がいい人：開放性と正直謙虚さが低い': classify(compatibility_4),
        '社会的手抜きを行う': classify(social_loafing),
        '同調圧力を感じやすい': classify(feel_peer_pressure),
        '高い学力になりやすい': classify(high_academic_performance),
        'オンライン学習が得意': classify(high_online_learning),
        '収入が高くなりやすい': classify(high_income),
        '仕事のパフォーマンスが高くなりやすい': classify(high_job_performance),
        'キャリアが上手くいきやすい': classify(career_success),
        '複雑な仕事へ適応できる': classify(adapting_to_complex_work),
        'いいチームメンバーになる': classify(good_team),
        '自発的に離職しやすい': classify(resignation),
        '疲れやすい': classify(tired),
        'バーンアウトしやすい': classify(burn_out),
        'リモートワークで成果を出しやすい': classify(remote_work),
        'ワークエンゲージメントが高くなりやすい': classify(engagement),
        '組織に帰属意識や愛着を持つ': classify(organizational_commitment),
        '職務の範囲外の仕事を積極的に行う': classify(ocb),
        '同僚や他の個人を自発的に助ける': classify(ocb_individual),
        '自発的に組織全体の利益になることを行う': classify(ocb_organization),
        '組織や業務プロセスの改善・変革を目指す': classify(ocb_change),
        '対人関係タスクが得意': classify(interpersonal_task),
        '深く学んで適応することができる': classify(learning_goal_orientation),
        '表面的な学習や見方、対応になる時がある': classify(surface_learning),
        'コーチングを行うと効果が出やすい': classify(effective_coaching),
        'グループや職務の境界を乗り越えて仕事を行う': classify(job_crafting),
        '新規事業や起業が得意': classify(entrepreneur_innovative_mind),
        'いい上司になりやすい': classify(supportive_boss),
        '変革型リーダーシップ': classify(leadership_transformational),
        '放任型リーダーシップ': classify(leadership_laissez_faire),
        '破壊型リーダーシップ': classify(leadership_destructive),
        'ビジョンのあるリーダーが好き': classify(followership_transformational),
        'フレンドリーなリーダーが好き': classify(followership_relational),
        '現実的なリーダーが好き': classify(followership_realistic)
    })

# 各行に対して指標を計算
indicators = data.apply(calculate_indicators, axis=1)

# 元のデータフレームと指標を結合
output_data = pd.concat([data, indicators], axis=1)

# 結果をoutput.csvとして保存
output_file_path = 'csv/output.csv'  # 出力ファイルのパス
output_data.to_csv(output_file_path, index=False)

print(f"結果が '{output_file_path}' に保存されました。")
