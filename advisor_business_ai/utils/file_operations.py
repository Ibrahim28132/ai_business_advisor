import os
from datetime import datetime
from utils.config import config
from utils.logging import logger


def break_long_words(line: str, max_word_length: int = 80) -> str:
    """
    Break long unbroken strings (like URLs or tokens).
    """
    safe_words = []
    for word in line.split():
        if len(word) > max_word_length:
            broken = [word[i:i + max_word_length] for i in range(0, len(word), max_word_length)]
            safe_words.extend(broken)
        else:
            safe_words.append(word)
    return ' '.join(safe_words)


def clean_problematic_lines(content: str) -> str:
    """
    Remove or clean markdown tables and overly wide lines.
    """
    clean_lines = []
    for line in content.split("\n"):
        if "|---" in line or line.strip().startswith("|"):
            continue
        clean_lines.append(line)
    return "\n".join(clean_lines)


def save_as_text(content: str, filename_prefix: str) -> str:
    try:
        output_dir = config.OUTPUT_DIR
        os.makedirs(output_dir, exist_ok=True)

        content = clean_problematic_lines(content)

        # Break long words in all lines
        cleaned_lines = []
        for line in content.split("\n"):
            line = line.strip()
            if not line:
                cleaned_lines.append("")
                continue
            safe_line = break_long_words(line)
            cleaned_lines.append(safe_line)

        full_text = "\n".join(cleaned_lines)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{filename_prefix}_{timestamp}.txt"
        filepath = os.path.join(output_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(full_text)

        return filepath

    except Exception as e:
        logger.error(f"Failed to save text file: {e}")
        return None



