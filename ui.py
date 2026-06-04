import customtkinter as ctk
import re
from quiz_brain import QuizBrain

# Set appearance mode (light/dark). CustomTkinter provides a global appearance setting;
# classic tkinter does not have a built-in global appearance mode.
ctk.set_appearance_mode("dark")
# Set default color theme for CTk widgets (no direct equivalent in classic tkinter)
ctk.set_default_color_theme("blue")


class QuizInterface:

    def __init__(self, quiz_brain: QuizBrain):
        self.quiz = quiz_brain

        # Main window: CTk replaces Tk for themed widgets.
        # Equivalent in tkinter: root = Tk()
        self.window = ctk.CTk()
        self.window.title("Quizier")
        # geometry behaves the same as in tkinter
        self.window.geometry("520x520")
        self.window.resizable(False, False)
        # grid_columnconfigure works the same as in tkinter
        self.window.grid_columnconfigure(0, weight=1)

        # Header container: CTkFrame is like tkinter.Frame but with styling options
        self.header_frame = ctk.CTkFrame(
            self.window, fg_color="#2f5161", corner_radius=15
        )
        self.header_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        self.header_frame.grid_columnconfigure((0, 1), weight=1)

        # Title label: CTkLabel ~ tkinter.Label but supports text_color and CTkFont
        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="Quizier",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="white",
        )
        self.title_label.grid(row=0, column=0, padx=(20, 0), pady=20, sticky="w")

        # Score label: same role as tkinter.Label
        self.score_label = ctk.CTkLabel(
            self.header_frame,
            text="Score: 0",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="white",
        )
        self.score_label.grid(row=0, column=1, padx=(0, 20), pady=20, sticky="e")

        # Question card: using CTkFrame + CTkLabel instead of a Canvas
        # Note: original tkinter UI used Canvas.create_text; here we rely on CTkLabel
        # for easier styling and wrapping.
        self.question_card = ctk.CTkFrame(
            self.window, fg_color="white", corner_radius=20
        )
        self.question_card.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.question_card.grid_rowconfigure(0, weight=1)
        self.question_card.grid_columnconfigure(0, weight=1)

        # Question label: CTkLabel with wraplength to limit line width.
        # We also add a helper that inserts soft-breaks into very long words so
        # they can wrap instead of overflowing the label bounds.
        self.question_label = ctk.CTkLabel(
            self.question_card,
            text="Press a button to begin the quiz.",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#375362",
            wraplength=460,
            justify="center",
        )
        self.question_label.grid(row=0, column=0, padx=30, pady=40, sticky="nsew")

        # Progress label (equivalent to a normal Label)
        self.progress_label = ctk.CTkLabel(
            self.window,
            text="Question 0/0",
            font=ctk.CTkFont(size=14),
            text_color="#5d7a8f",
        )
        self.progress_label.grid(row=2, column=0, pady=(0, 5))

        # Progress bar: CTkProgressBar ~ ttk.Progressbar. Use .set(value) to update.
        self.progress_bar = ctk.CTkProgressBar(self.window, width=460)
        self.progress_bar.set(0)
        self.progress_bar.grid(row=3, column=0, pady=(0, 15))

        # Buttons container
        self.buttons_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        self.buttons_frame.grid(row=4, column=0, pady=10, sticky="ew")
        self.buttons_frame.grid_columnconfigure((0, 1), weight=1)

        # True button: CTkButton mirrors tkinter.Button with extra styling
        self.true_button = ctk.CTkButton(
            self.buttons_frame,
            text="True",
            fg_color="#28a745",
            hover_color="#209a37",
            command=self.true_pressed,
            corner_radius=15,
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        self.true_button.grid(row=0, column=0, padx=(20, 10), pady=10, sticky="ew")

        # False button
        self.false_button = ctk.CTkButton(
            self.buttons_frame,
            text="False",
            fg_color="#dc3545",
            hover_color="#b32b3b",
            command=self.false_pressed,
            corner_radius=15,
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        self.false_button.grid(row=0, column=1, padx=(10, 20), pady=10, sticky="ew")

        self.get_next_question()
        self.window.mainloop()

    def _insert_breaks(self, text: str, max_len: int = 40) -> str:
        """Insert soft-breaks (zero-width space) into very long words so labels can wrap.

        Some quiz questions may contain very long continuous strings (URLs or no-space
        sequences) that prevent normal wrapping. This helper inserts a zero-width space
        every `max_len` characters inside long words to allow the label to break lines.
        """
        if not text:
            return text

        def repl(match):
            word = match.group(0)
            parts = [word[i : i + max_len] for i in range(0, len(word), max_len)]
            return "\u200b".join(parts)

        # Find sequences of non-whitespace characters longer than max_len
        pattern = r"\S{" + str(max_len) + r",}"
        return re.sub(pattern, repl, text)

    def get_next_question(self):
        self.question_card.configure(fg_color="white")
        if self.quiz.still_has_questions():
            self.score_label.configure(text=f"Score: {self.quiz.score}")
            self.progress_label.configure(
                text=f"Question {self.quiz.question_number + 1}/{len(self.quiz.question_list)}"
            )
            progress_value = self.quiz.question_number / len(self.quiz.question_list)
            self.progress_bar.set(progress_value)
            q_text = self.quiz.next_question()
            # Prevent long unbroken words from overflowing by inserting soft-breaks
            q_text = self._insert_breaks(q_text, max_len=40)
            self.question_label.configure(text=q_text, text_color="#375362")
            self.true_button.configure(state="normal")
            self.false_button.configure(state="normal")
        else:
            self.question_label.configure(text="َYou've reached the end of the quiz!", text_color="#375362")
            self.progress_label.configure(
                text=f"Final score: {self.quiz.score}/{len(self.quiz.question_list)}"
            )
            self.progress_bar.set(1.0)
            self.true_button.configure(state="disabled")
            self.false_button.configure(state="disabled")

    def true_pressed(self):
        self.give_feedback(self.quiz.check_answer("True"))

    def false_pressed(self):
        self.give_feedback(self.quiz.check_answer("False"))

    def give_feedback(self, is_right):
        if is_right:
            self.question_card.configure(fg_color="#d4f5e9")
            self.question_label.configure(text_color="#1f7a45")
        else:
            self.question_card.configure(fg_color="#f8d7da")
            self.question_label.configure(text_color="#8a1f2f")
        self.window.after(700, self.get_next_question)
