from __future__ import annotations

import os

import requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput

API = os.environ.get("SOVEREIGN_API", "http://127.0.0.1:8000")
TOKEN = os.environ.get("SOVEREIGN_TRIGGER_TOKEN", "change-me-to-a-long-random-value")


class SovereignUI(App):
    def build(self):
        layout = BoxLayout(orientation="vertical", padding=12, spacing=8)
        self.title_label = Label(text="Sovereign Intelligence OS — Fold 7", size_hint_y=0.1)
        self.input = TextInput(multiline=True, hint_text="Ask anything...", size_hint_y=0.5)
        self.output = Label(text="", size_hint_y=0.3)
        send = Button(text="Send to orchestrator", size_hint_y=0.1)
        send.bind(on_press=self.send_to_orchestrator)
        layout.add_widget(self.title_label)
        layout.add_widget(self.input)
        layout.add_widget(send)
        layout.add_widget(self.output)
        return layout

    def send_to_orchestrator(self, _instance):
        query = self.input.text.strip()
        if not query:
            self.output.text = "(empty query)"
            return
        try:
            response = requests.post(
                f"{API}/trigger",
                json={"query": query, "gesture": "tap", "context": "kivy"},
                headers={"x-sovereign-token": TOKEN},
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
            self.output.text = (data.get("content") or data.get("error") or "(empty)")[:800]
        except requests.RequestException as exc:
            self.output.text = f"error: {exc}"


if __name__ == "__main__":
    SovereignUI().run()
