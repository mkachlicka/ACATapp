import customtkinter as ctk

from acat.backend.judge_score import LanguageModel


class ModelComboChooser(ctk.CTkComboBox):
    """Dropdown for selecting the language model used for scoring."""

    def __init__(self, *args, **kwargs):
        models = [m.value for m in LanguageModel]
        super().__init__(*args, values=models, state="readonly", **kwargs)
        self.set(models[0])

    def get_model(self) -> LanguageModel:
        return LanguageModel(self.get())
