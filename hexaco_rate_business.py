import pandas as pd

# data.csvを読み込む
file_path = 'data.csv'  # あなたのファイルのパスを指定
data = pd.read_csv(file_path)

# 閾値の設定
l = 0.4  # low threshold
h = 0.65  # high threshold


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
                + (0.2 if row['Conscientiousness'] <= 3.0 else 0)
    machiavellianism = (0.3 if row['Honesty-Humility'] <= 2.5 else 0) \
                    + (0.3 if row['Agreeableness'] <= 2.5 else 0) \
                    + (0.2 if row['Emotionality'] <= 3.0 else 0) \
                    + (0.2 if row['Extraversion'] <= 3.0 else 0) \
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
    effort = 1 if row['Conscientiousness'] >= 4 else 0
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
    listening_to_others = 1 if row['Extraversion'] <= 3 else 0
    adapting_to_change = 1 if row['Extraversion'] <= 3 else 0
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
                    + (0.34 if row['Emotionality'] <= 3 else 0)
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
    risk_humble_calm = 1 if row['Conscientiousness'] >= 4 else 0
    risk_low_regret = 1 if row['Openness'] >= 4 else 0

    risk_challenge = (0.6 if row['Openness'] >= 4 else 0) \
                    + (0.4 if row['Conscientiousness'] <= 3 else 0)
    risk_strong_bias = 1 if row['Emotionality'] >= 4 else 0
    
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
    like_philanthropy = 1 if row['Agreeableness'] >= 4 else 0
    like_harmony = (0.33 if row['Extraversion'] <= 3 else 0) \
                + (0.33 if row['Openness'] <= 3 else 0) \
                + (0.34 if row['Agreeableness'] >= 4 else 0)
    like_tradition = (0.33 if row['Extraversion'] <= 3 else 0) \
                    + (0.33 if row['Openness'] <= 3 else 0) \
                    + (0.34 if row['Agreeableness'] >= 4 else 0)
    like_safety = (0.5 if row['Openness'] <= 3 else 0) \
                + (0.5 if row['Conscientiousness'] >= 4 else 0)
    politics_left = 1 if row['Openness'] >= 4 else 0
    politics_right = (0.33 if row['Honesty-Humility'] <= 3 else 0) \
                    + (0.33 if row['Openness'] <= 3 else 0) \
                    + (0.34 if row['Conscientiousness'] >= 4 else 0)
    proenvironmental_attitudes = (0.5 if row['Honesty-Humility'] >= 4 else 0) \
                                + (0.5 if row['Openness'] >= 4 else 0)
    prejudice_rwa = (0.5 if row['Conscientiousness'] >= 4 else 0) \
                    + (0.5 if row['Openness'] <= 3 else 0)
    prejudice_sdo = 1 if row['Agreeableness'] <= 3 else 0
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
    social_loafing = 1 if row['Conscientiousness'] <= 3 else 0
    feel_peer_pressure = (0.25 if row['Extraversion'] >= 4 else 0) \
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

    adapting_to_complex_work = 1 if row['Extraversion'] <= 3 else 0
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
    followership_transformational = (0.33 if row['Emotionality'] >= 4 else 0) \
                                + (0.33 if row['Extraversion'] >= 4 else 0) \
                                + (0.34 if row['Openness'] >= 4 else 0)
    followership_relational = 1 if row['Emotionality'] >= 4 else 0
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
        'dark_trend': classify(dark_trend),
        'narcissism': classify(narcissism),
        'psychopathy': classify(psychopathy),
        'machiavellianism': classify(machiavellianism),
        'highIQ': classify(highIQ),
        'highEQ': classify(highEQ),
        'critical_thinking': classify(critical_thinking),
        'effort': classify(effort),
        'high_motivation': classify(high_motivation),
        'sdt_autonomy': classify(sdt_autonomy),
        'sdt_competent': classify(sdt_competent),
        'sdt_relation': classify(sdt_relation),
        'listening_to_others': classify(listening_to_others),
        'adapting_to_change': classify(adapting_to_change),
        'feel_happiness': classify(feel_happiness),
        'feel_lucky': classify(feel_lucky),
        'high_self_efficacy': classify(high_self_efficacy),
        'positive_thinking': classify(positive_thinking),
        'resilience': classify(resilience),
        'coping_problem_solving': classify(coping_problem_solving),
        'coping_emotional_support': classify(coping_emotional_support),
        'coping_recreation': classify(coping_recreation),
        'coping_cognitive_restructuring': classify(coping_cognitive_restructuring),
        'coping_acceptance': classify(coping_acceptance),
        'coping_avoidance': classify(coping_avoidance),
        'coping_denial': classify(coping_denial),
        'coping_wishful_thinking': classify(coping_wishful_thinking),
        'coping_withdrawal': classify(coping_withdrawal),
        'coping_negative_emotion': classify(coping_negative_emotion),
        'coping_substance_use': classify(coping_substance_use),
        'coping_religious': classify(coping_religious),
        'risk_humble_calm': classify(risk_humble_calm),
        'risk_low_regret': classify(risk_low_regret),
        'risk_challenge': classify(risk_challenge),
        'risk_strong_bias': classify(risk_strong_bias),
        'spirituality': classify(spirituality),
        'like_power': classify(like_power),
        'like_achievement': classify(like_achievement),
        'like_pleasure': classify(like_pleasure),
        'like_exciting': classify(like_exciting),
        'like_independence': classify(like_independence),
        'like_universal': classify(like_universal),
        'like_philanthropy': classify(like_philanthropy),
        'like_harmony': classify(like_harmony),
        'like_tradition': classify(like_tradition),
        'like_safety': classify(like_safety),
        'politics_left': classify(politics_left),
        'politics_right': classify(politics_right),
        'proenvironmental_attitudes': classify(proenvironmental_attitudes),
        'prejudice_rwa': classify(prejudice_rwa),
        'prejudice_sdo': classify(prejudice_sdo),
        'beliefin_unjust_world': classify(beliefin_unjust_world),
        'compatibility_1': classify(compatibility_1),
        'compatibility_2': classify(compatibility_2),
        'compatibility_3': classify(compatibility_3),
        'compatibility_4': classify(compatibility_4),
        'social_loafing': classify(social_loafing),
        'feel_peer_pressure': classify(feel_peer_pressure),
        'high_academic_performance': classify(high_academic_performance),
        'high_online_learning': classify(high_online_learning),
        'high_income': classify(high_income),
        'high_job_performance': classify(high_job_performance),
        'career_success': classify(career_success),
        'adapting_to_complex_work': classify(adapting_to_complex_work),
        'good_team': classify(good_team),
        'resignation': classify(resignation),
        'tired': classify(tired),
        'burn_out': classify(burn_out),
        'remote_work': classify(remote_work),
        'engagement': classify(engagement),
        'organizational_commitment': classify(organizational_commitment),
        'ocb': classify(ocb),
        'ocb_individual': classify(ocb_individual),
        'ocb_organization': classify(ocb_organization),
        'ocb_change': classify(ocb_change),
        'interpersonal_task': classify(interpersonal_task),
        'learning_goal_orientation': classify(learning_goal_orientation),
        'surface_learning': classify(surface_learning),
        'effective_coaching': classify(effective_coaching),
        'job_crafting': classify(job_crafting),
        'entrepreneur_innovative_mind': classify(entrepreneur_innovative_mind),
        'supportive_boss': classify(supportive_boss),
        'leadership_transformational': classify(leadership_transformational),
        'leadership_laissez_faire': classify(leadership_laissez_faire),
        'leadership_destructive': classify(leadership_destructive),
        'followership_transformational': classify(followership_transformational),
        'followership_relational': classify(followership_relational),
        'followership_realistic': classify(followership_realistic)
    })

# 各行に対して指標を計算
indicators = data.apply(calculate_indicators, axis=1)

# 元のデータフレームと指標を結合
output_data = pd.concat([data, indicators], axis=1)

# 結果をoutput.csvとして保存
output_file_path = 'output.csv'  # 出力ファイルのパス
output_data.to_csv(output_file_path, index=False)

print(f"結果が '{output_file_path}' に保存されました。")
