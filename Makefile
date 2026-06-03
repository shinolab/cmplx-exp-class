PY      := uv run python
MARP    := marp
THEME   := slides/theme/main.css
MARPOPT := --allow-local-files --theme-set $(THEME)
OUT     := out

.PHONY: all figures pdf watch setup clean

all: figures pdf

setup:
	uv sync

figures:
	$(PY) scripts/gen_figures.py

pdf: $(OUT)
	$(MARP) slides/session1.md -o $(OUT)/session1.pdf $(MARPOPT)

html: $(OUT)
	$(MARP) slides/session1.md -o $(OUT)/session1.html $(MARPOPT)
	cp -r slides/figures $(OUT)/figures

watch:
	$(MARP) -s slides $(MARPOPT)

$(OUT):
	mkdir -p $(OUT)

clean:
	rm -rf $(OUT)
