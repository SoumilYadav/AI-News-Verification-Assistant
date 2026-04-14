import tkinter as tk
from tkinter import scrolledtext
import re

TRUSTED_SOURCES = [
    "bbc", "reuters", "associated press", "ap news", "the hindu",
    "indian express", "ndtv", "times of india", "hindustan times",
    "cnn", "al jazeera", "npr", "the guardian"
]

SUSPICIOUS_PHRASES = [
    "shocking truth", "you won't believe", "must watch", "forward this",
    "share this now", "they don't want you to know", "miracle cure",
    "100% guaranteed", "secret revealed", "breaking!!!", "urgent!!!",
    "click here", "exclusive leak", "viral message", "spread this",
    "hidden truth", "what happened next", "unbelievable", "end is near"
]

SENSATIONAL_WORDS = [
    "shocking", "unbelievable", "urgent", "explosive", "miracle",
    "disaster", "massive", "sensational", "scandal", "panic",
    "terrifying", "exposed", "secret", "viral", "breaking"
]

EMOTIONAL_WORDS = [
    "hate", "fear", "anger", "panic", "disgusting", "betrayal",
    "destroy", "attack", "danger", "threat", "horrific"
]


def count_matches(text, word_list):
    count = 0
    found = []
    lower_text = text.lower()
    for word in word_list:
        if word in lower_text:
            count += lower_text.count(word)
            found.append(word)
    return count, found


def analyze_news(text):
    text = text.strip()

    if not text:
        return {
            "verdict": "No Input",
            "score": 0,
            "confidence": 0,
            "reasons": ["Please enter a news headline or article."],
            "tips": []
        }

    score = 50  # neutral starting credibility
    reasons = []
    tips = []

    lower_text = text.lower()
    words = re.findall(r"\b\w+\b", text)
    word_count = len(words)

    suspicious_count, suspicious_found = count_matches(text, SUSPICIOUS_PHRASES)
    sensational_count, sensational_found = count_matches(text, SENSATIONAL_WORDS)
    emotional_count, emotional_found = count_matches(text, EMOTIONAL_WORDS)
    trusted_count, trusted_found = count_matches(text, TRUSTED_SOURCES)

    exclamations = text.count("!")
    question_marks = text.count("?")
    all_caps_words = re.findall(r"\b[A-Z]{3,}\b", text)
    urls = re.findall(r"https?://\S+|www\.\S+", text)

    # Positive signals
    if trusted_count > 0:
        score += 20
        reasons.append(f"Trusted source reference found: {', '.join(set(trusted_found))}.")
    else:
        reasons.append("No clearly trusted source was identified.")

    if urls:
        score += 5
        reasons.append("The text contains a link/source reference.")
    else:
        reasons.append("No link or source reference was found.")

    if word_count >= 30:
        score += 5
        reasons.append("The content has some detail, which can indicate better credibility.")
    else:
        reasons.append("The content is very short, which makes verification harder.")

    # Negative signals
    if suspicious_count > 0:
        penalty = min(20, suspicious_count * 5)
        score -= penalty
        reasons.append(
            f"Suspicious clickbait phrases detected: {', '.join(set(suspicious_found))}."
        )

    if sensational_count > 0:
        penalty = min(15, sensational_count * 3)
        score -= penalty
        reasons.append(
            f"Sensational wording detected: {', '.join(set(sensational_found))}."
        )

    if emotional_count > 0:
        penalty = min(10, emotional_count * 2)
        score -= penalty
        reasons.append(
            f"Highly emotional language detected: {', '.join(set(emotional_found))}."
        )

    if exclamations >= 3:
        score -= 10
        reasons.append(f"Too many exclamation marks detected ({exclamations}).")

    if question_marks >= 3:
        score -= 5
        reasons.append(f"Too many question marks detected ({question_marks}).")

    if len(all_caps_words) >= 3:
        score -= 10
        reasons.append(
            f"Excessive ALL-CAPS words detected: {', '.join(all_caps_words[:6])}."
        )

    if "forward this" in lower_text or "share this" in lower_text:
        score -= 10
        reasons.append("Message urges users to forward/share quickly, which is common in fake news.")

    if re.search(r"\b(guaranteed|confirmed by everyone|absolutely true|100% true)\b", lower_text):
        score -= 10
        reasons.append("Overconfident certainty claims detected.")

    # Clamp score
    score = max(0, min(100, score))

    # Verdict
    if score >= 70:
        verdict = "Likely Real"
    elif score >= 40:
        verdict = "Suspicious / Needs Verification"
    else:
        verdict = "Likely Fake"

    confidence = abs(score - 50) * 2
    confidence = min(100, confidence)

    tips = [
        "Check the claim on trusted news websites.",
        "Verify whether the article mentions a reliable source.",
        "Be careful with emotional or sensational wording.",
        "Do not rely only on forwarded social media messages.",
        "Cross-check the same news with at least two trusted outlets."
    ]

    return {
        "verdict": verdict,
        "score": score,
        "confidence": confidence,
        "reasons": reasons,
        "tips": tips
    }


def run_analysis():
    input_text = news_input.get("1.0", tk.END)
    result = analyze_news(input_text)

    verdict_value.config(text=result["verdict"])
    score_value.config(text=f"{result['score']}/100")
    confidence_value.config(text=f"{result['confidence']}%")

    reasons_box.config(state=tk.NORMAL)
    reasons_box.delete("1.0", tk.END)
    reasons_box.insert(tk.END, "Reasons:\n\n")
    for idx, reason in enumerate(result["reasons"], start=1):
        reasons_box.insert(tk.END, f"{idx}. {reason}\n")
    reasons_box.insert(tk.END, "\nTips:\n\n")
    for idx, tip in enumerate(result["tips"], start=1):
        reasons_box.insert(tk.END, f"{idx}. {tip}\n")
    reasons_box.config(state=tk.DISABLED)


def clear_all():
    news_input.delete("1.0", tk.END)
    verdict_value.config(text="-")
    score_value.config(text="-")
    confidence_value.config(text="-")
    reasons_box.config(state=tk.NORMAL)
    reasons_box.delete("1.0", tk.END)
    reasons_box.config(state=tk.DISABLED)


# GUI
root = tk.Tk()
root.title("AI News Verification Assistant")
root.geometry("900x700")
root.configure(bg="#0f172a")

title = tk.Label(
    root,
    text="AI News Verification Assistant",
    font=("Arial", 22, "bold"),
    bg="#0f172a",
    fg="white"
)
title.pack(pady=15)

subtitle = tk.Label(
    root,
    text="Paste a news headline or article to check its credibility",
    font=("Arial", 11),
    bg="#0f172a",
    fg="#cbd5e1"
)
subtitle.pack()

input_frame = tk.Frame(root, bg="#0f172a")
input_frame.pack(pady=15)

news_input = scrolledtext.ScrolledText(
    input_frame,
    wrap=tk.WORD,
    width=90,
    height=12,
    font=("Arial", 11),
    bg="#e2e8f0",
    fg="black"
)
news_input.pack()

button_frame = tk.Frame(root, bg="#0f172a")
button_frame.pack(pady=10)

analyze_btn = tk.Button(
    button_frame,
    text="Analyze News",
    command=run_analysis,
    font=("Arial", 12, "bold"),
    bg="#22c55e",
    fg="white",
    width=15
)
analyze_btn.grid(row=0, column=0, padx=10)

clear_btn = tk.Button(
    button_frame,
    text="Clear",
    command=clear_all,
    font=("Arial", 12, "bold"),
    bg="#ef4444",
    fg="white",
    width=15
)
clear_btn.grid(row=0, column=1, padx=10)

result_frame = tk.Frame(root, bg="#1e293b", bd=2, relief=tk.RIDGE)
result_frame.pack(padx=20, pady=15, fill=tk.X)

tk.Label(result_frame, text="Verdict:", font=("Arial", 13, "bold"), bg="#1e293b", fg="white").grid(row=0, column=0, padx=20, pady=10, sticky="w")
verdict_value = tk.Label(result_frame, text="-", font=("Arial", 13), bg="#1e293b", fg="#38bdf8")
verdict_value.grid(row=0, column=1, padx=20, pady=10, sticky="w")

tk.Label(result_frame, text="Credibility Score:", font=("Arial", 13, "bold"), bg="#1e293b", fg="white").grid(row=1, column=0, padx=20, pady=10, sticky="w")
score_value = tk.Label(result_frame, text="-", font=("Arial", 13), bg="#1e293b", fg="#38bdf8")
score_value.grid(row=1, column=1, padx=20, pady=10, sticky="w")

tk.Label(result_frame, text="Confidence:", font=("Arial", 13, "bold"), bg="#1e293b", fg="white").grid(row=2, column=0, padx=20, pady=10, sticky="w")
confidence_value = tk.Label(result_frame, text="-", font=("Arial", 13), bg="#1e293b", fg="#38bdf8")
confidence_value.grid(row=2, column=1, padx=20, pady=10, sticky="w")

reasons_label = tk.Label(
    root,
    text="Analysis Details",
    font=("Arial", 16, "bold"),
    bg="#0f172a",
    fg="white"
)
reasons_label.pack(pady=(10, 5))

reasons_box = scrolledtext.ScrolledText(
    root,
    wrap=tk.WORD,
    width=95,
    height=16,
    font=("Arial", 11),
    bg="#e2e8f0",
    fg="black",
    state=tk.DISABLED
)
reasons_box.pack(padx=20, pady=10)

footer = tk.Label(
    root,
    text="AI Type: Rule-Based Expert System / Heuristic AI",
    font=("Arial", 10, "italic"),
    bg="#0f172a",
    fg="#94a3b8"
)
footer.pack(pady=8)

root.mainloop()