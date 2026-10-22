"""Configuration and the bakery seed taxonomy.

The seed terms drive two things:
  1. Query generation (what we go search for), and
  2. Term tagging (which known concepts show up in what we collect).

Edit these lists to steer the collector. Keep them lowercase; matching is
case-insensitive. Multi-word terms are matched as whole phrases.
"""

from __future__ import annotations

# The YouTube API key lives in trendbaker.config.settings (read from backend/.env),
# not here — this module is only collection defaults and the seed taxonomy.

# --- Collection defaults ----------------------------------------------------
DEFAULT_LOOKBACK_DAYS = 30          # how recent content must be to count as a "signal"
DEFAULT_MAX_PER_QUERY = 50          # video results per query (API max 50/page)
DEFAULT_ORDER = "relevance"         # relevance | date | viewCount | rating
DEFAULT_REGIONS = ["US"]            # ISO codes; add e.g. "GB","CA","AU" for regional trends
FETCH_COMMENTS = False              # comments add quota cost; off by default
COMMENTS_PER_VIDEO = 20

# --- Bakery taxonomy (seed terms) -------------------------------------------
FORMATS = [
    # hybrids & viral formats
    "crookie", "cruffin", "cronut", "cube croissant",
    "flat croissant", "kouign-amann", "basque cheesecake", "canele",
    # cookies & bars
    "cookie", "ny cookie", "brownie", "blondie", "cookie pie", "pop tart",
    # laminated & enriched
    "croissant", "laminated dough", "danish", "brioche", "babka",
    "cinnamon roll", "cinnamon bun", "kanelbulle",
    # breads
    "sourdough", "focaccia", "bagel", "milk bread", "shokupan", "concha",
    "banana bread", "cottage cheese bread",
    # cakes & pastry
    "cupcake", "muffin", "tart", "galette", "tres leches", "madeleine",
    "cake", "loaf cake", "pie", "scone", "donut", "doughnut", "pretzel",
]

FLAVOURS = [
    # hero trend flavours
    "dubai chocolate", "pistachio", "matcha", "strawberry matcha", "ube",
    "black sesame", "biscoff", "lotus", "tahini", "miso", "brown butter",
    # tea & aromatic
    "yuzu", "pandan", "hojicha", "earl grey", "london fog", "chai",
    "cardamom", "saffron", "rose", "lavender",
    # sweet & classic
    "salted caramel", "tiramisu", "espresso", "coffee", "cookie butter",
    "birthday cake", "funfetti", "hot honey", "maple", "lemon", "raspberry",
    "blueberry", "hazelnut", "halva",
]

INGREDIENTS = [
    # trend-defining
    "kataifi", "pistachio cream", "sourdough starter", "sourdough discard",
    "tangzhong", "cottage cheese", "greek yogurt", "protein powder",
    # flours & grains
    "almond flour", "oat flour", "oat milk", "chickpea flour", "bean flour",
    "einkorn", "spelt flour", "rye flour",
    # fats, dairy & sweeteners
    "brown butter", "olive oil", "cream cheese", "mascarpone", "ricotta",
    "condensed milk", "nutella", "gianduja", "dark chocolate",
    "flaky sea salt", "sea salt", "honey", "dates", "date syrup",
    "monk fruit", "allulose", "erythritol",
    # aromatics
    "cinnamon", "vanilla bean", "tahini", "freeze-dried fruit",
]

# Modifiers appended to seed terms to surface *emerging* / recipe content.
QUERY_MODIFIERS = ["recipe", "trend", "viral", "new", "2026"]

# Keys are singular to match models.Category and the item_terms.category column.
SEED_CATEGORIES: dict[str, list[str]] = {
    "format": FORMATS,
    "flavour": FLAVOURS,
    "ingredient": INGREDIENTS,
}