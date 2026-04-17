def safety_check(answer):
    banned = ["guaranteed cure", "100% safe", "take exactly"]
    for b in banned:
        if b in answer.lower():
            return "Please consult a qualified doctor for safe medical advice."
    return answer