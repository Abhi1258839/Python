import pygame
import sys
import json
import os
import time
import random
import math

# --- Initialization ---
pygame.init()
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ultimate Business Empire")

# Colors
WHITE, BLACK = (245, 245, 250), (20, 20, 20)
GREEN, DARK_GREEN = (76, 175, 80), (56, 142, 60)
BLUE, DARK_BLUE = (33, 150, 243), (25, 118, 210)
GRAY, DARK_GRAY = (200, 200, 200), (150, 150, 150)
GOLD = (255, 215, 0)
RED = (244, 67, 54)
PURPLE = (156, 39, 176)
CYAN = (0, 255, 255)

# Fonts
font_large = pygame.font.SysFont("arial", 48, bold=True)
font_medium = pygame.font.SysFont("arial", 24, bold=True)
font_small = pygame.font.SysFont("arial", 16)

# --- Procedural Generation of 100+ Luxury Assets ---
luxury_pool = {}
# Generate 34 Watches, 34 Cars, 34 Mansions (102 Total Items)
for i in range(1, 35):
    luxury_pool[f"Watch Tier {i}"] = {"cost": 5000 * (1.4**i), "boost": 0.02, "owned": 0, "type": "Watch"}
for i in range(1, 35):
    luxury_pool[f"Supercar Tier {i}"] = {"cost": 50000 * (1.5**i), "boost": 0.05, "owned": 0, "type": "Car"}
for i in range(1, 35):
    luxury_pool[f"Mansion Tier {i}"] = {"cost": 1000000 * (1.6**i), "boost": 0.15, "owned": 0, "type": "Real Estate"}

# --- Game State ---
SAVE_FILE = "ultimate_empire.json"
current_tab = "Main"
scroll_y = 0 # For scrolling lists

state = {
    "money": 0.0,
    "bank_balance": 0.0, # New: Bank System
    "lifetime_money": 0.0,
    "click_value": 1.0,
    "click_upgrade_cost": 20.0,
    "prestige_multiplier": 1.0,
    "last_played": time.time(),
    "businesses": {
        "Lemonade Stand": {"cost": 50, "base_income": 2, "owned": 0, "milestone_mult": 1, "has_manager": False},
        "Tech Startup": {"cost": 500, "base_income": 25, "owned": 0, "milestone_mult": 1, "has_manager": False},
        "Real Estate": {"cost": 5000, "base_income": 300, "owned": 0, "milestone_mult": 1, "has_manager": False},
        "Bank": {"cost": 50000, "base_income": 4000, "owned": 0, "milestone_mult": 1, "has_manager": False},
        "Aerospace": {"cost": 1000000, "base_income": 50000, "owned": 0, "milestone_mult": 1, "has_manager": False}
    },
    "markets": {
        "Stocks (TechCorp)": {"price": 100.0, "owned": 0, "volatility": 0.1},
        "Stocks (GoldMines)": {"price": 500.0, "owned": 0, "volatility": 0.05},
        "Crypto (DogeCoin)": {"price": 10.0, "owned": 0, "volatility": 0.4}, # New: High volatility
        "Crypto (BitCoin)": {"price": 30000.0, "owned": 0, "volatility": 0.25}
    },
    "luxuries": luxury_pool
}

# Load Game
if os.path.exists(SAVE_FILE):
    try:
        with open(SAVE_FILE, "r") as f:
            loaded_state = json.load(f)
            for key in loaded_state:
                if key in state and isinstance(state[key], dict):
                    state[key].update(loaded_state[key])
                else:
                    state[key] = loaded_state[key]
    except Exception:
        pass

def save_game():
    state["last_played"] = time.time()
    with open(SAVE_FILE, "w") as f:
        json.dump(state, f)

# --- Helpers ---
class Particle:
    def __init__(self, x, y, text, color):
        self.x, self.y, self.text, self.color, self.alpha = x, y, text, color, 255
        self.surf = font_medium.render(self.text, True, self.color).convert_alpha()
    def update_and_draw(self, surface):
        self.y -= 2
        self.alpha -= 5
        self.surf.set_alpha(max(0, self.alpha))
        surface.blit(self.surf, (self.x, self.y))

class Button:
    def __init__(self, x, y, w, h, text, color, hover_color, text_color=WHITE, font=font_medium):
        self.rect = pygame.Rect(x, y, w, h)
        self.text, self.color, self.hover_color = text, color, hover_color
        self.text_color, self.font = text_color, font

    def draw(self, surface, offset_y=0):
        adjusted_rect = self.rect.move(0, offset_y)
        mouse_pos = pygame.mouse.get_pos()
        current_color = self.hover_color if adjusted_rect.collidepoint(mouse_pos) else self.color
        
        pygame.draw.rect(surface, current_color, adjusted_rect, border_radius=5)
        pygame.draw.rect(surface, BLACK, adjusted_rect, 2, border_radius=5)
        
        lines = self.text.split('\n')
        for i, line in enumerate(lines):
            text_surf = self.font.render(line, True, self.text_color)
            text_rect = text_surf.get_rect(center=(adjusted_rect.centerx, adjusted_rect.y + (adjusted_rect.height / (len(lines)+1)) * (i+1)))
            surface.blit(text_surf, text_rect)

    def is_clicked(self, event, offset_y=0):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.move(0, offset_y).collidepoint(event.pos)
        return False

# --- Core Mechanics ---
def get_luxury_multiplier():
    mult = 1.0
    for lux in state["luxuries"].values():
        if lux["owned"] > 0:
            mult += lux["boost"]
    return mult

def get_idle_income():
    income = 0
    for biz in state["businesses"].values():
        biz_income = biz["base_income"] * biz["owned"] * biz["milestone_mult"]
        if biz["has_manager"]: biz_income *= 1.5 # Managers give 50% boost
        income += biz_income
    
    gross_income = income * state["prestige_multiplier"] * get_luxury_multiplier()
    # 5% Tax/Upkeep deduction
    net_income = gross_income * 0.95 
    return net_income

def add_money(amount):
    state["money"] += amount
    state["lifetime_money"] += max(0, amount)

def get_prestige_gain():
    return max(0, math.floor(math.sqrt(state["lifetime_money"] / 100000)))

# --- Events & Timers ---
IDLE_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(IDLE_EVENT, 1000)

MARKET_EVENT = pygame.USEREVENT + 2
pygame.time.set_timer(MARKET_EVENT, 2000) # Markets update fast!

BANK_EVENT = pygame.USEREVENT + 3
pygame.time.set_timer(BANK_EVENT, 5000) # Bank pays interest every 5 seconds

SAVE_EVENT = pygame.USEREVENT + 4
pygame.time.set_timer(SAVE_EVENT, 10000)

# News Ticker setup
news_headlines = ["Stocks are booming!", "Crypto is crashing!", "Local Lemonade stand goes public.", "Billionaire buys 10th yacht.", "Taxes lowered for the rich!"]
news_x = WIDTH
current_news = random.choice(news_headlines)

particles = []
clock = pygame.time.Clock()
running = True

# Tab Buttons
tabs = ["Main", "Businesses", "Markets", "Luxury"]
tab_buttons = []
for i, tab in enumerate(tabs):
    tab_buttons.append(Button(250 + (i * 200), 80, 180, 40, tab, DARK_GRAY, GRAY, BLACK))

# --- Main Game Loop ---
while running:
    screen.fill(WHITE)
    mouse_pos = pygame.mouse.get_pos()
    current_income = get_idle_income()
    click_power = state["click_value"] * state["prestige_multiplier"] * get_luxury_multiplier()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_game()
            running = False

        # Scrolling
        if event.type == pygame.MOUSEWHEEL:
            scroll_y += event.y * 30
            scroll_y = min(0, scroll_y) # Prevent scrolling down past the top

        if event.type == IDLE_EVENT:
            add_money(current_income)

        if event.type == MARKET_EVENT:
            for s in state["markets"].values():
                change = random.uniform(-s["volatility"], s["volatility"])
                s["price"] = max(1.0, s["price"] * (1 + change))

        if event.type == BANK_EVENT:
            # 2% interest on bank balance
            interest = state["bank_balance"] * 0.02
            state["bank_balance"] += interest

        if event.type == SAVE_EVENT:
            save_game()

        # Tab Switching
        for i, btn in enumerate(tab_buttons):
            if btn.is_clicked(event):
                current_tab = tabs[i]
                scroll_y = 0 # Reset scroll on tab switch

        # --- TAB: MAIN ---
        if current_tab == "Main":
            btn_main_click = Button(WIDTH//2 - 150, 250, 300, 150, f"CLICK\n(+${click_power:,.2f})", GREEN, DARK_GREEN)
            if btn_main_click.is_clicked(event):
                add_money(click_power)
                particles.append(Particle(mouse_pos[0], mouse_pos[1]-20, f"+${click_power:,.1f}", DARK_GREEN))

            btn_upg_click = Button(WIDTH//2 - 150, 420, 300, 60, f"Upgrade Click\nCost: ${state['click_upgrade_cost']:,.0f}", BLUE, DARK_BLUE, font=font_small)
            if btn_upg_click.is_clicked(event) and state["money"] >= state["click_upgrade_cost"]:
                state["money"] -= state["click_upgrade_cost"]
                state["click_value"] *= 2
                state["click_upgrade_cost"] *= 2.2

            btn_vc = Button(WIDTH//2 - 150, 500, 300, 60, f"Venture Capital Funding\n(+${current_income * 60:,.0f} Instantly)", PURPLE, (120, 30, 140), font=font_small)
            if btn_vc.is_clicked(event):
                add_money(current_income * 60)
                particles.append(Particle(WIDTH//2, 500, "VC FUNDING SECURED!", PURPLE))

            prestige_gain = get_prestige_gain()
            btn_prestige = Button(WIDTH//2 - 150, 600, 300, 80, f"SELL EMPIRE (PRESTIGE)\nGain +{prestige_gain}% Global Bonus", RED, (200, 50, 50), font=font_small)
            if btn_prestige.is_clicked(event) and prestige_gain > 0:
                state["prestige_multiplier"] += (prestige_gain / 100.0)
                state["money"] = 0
                state["businesses"] = {k: {"cost": v["cost"], "base_income": v["base_income"], "owned": 0, "milestone_mult": 1, "has_manager": False} for k, v in state["businesses"].items()}

        # --- TAB: BUSINESSES ---
        elif current_tab == "Businesses":
            y_offset = 200
            for name, b in state["businesses"].items():
                btn_buy = Button(200, y_offset, 400, 80, f"{name} (Own: {b['owned']})\nCost: ${b['cost']:,.0f} | +${b['base_income']*b['milestone_mult']:,.0f}/s", GRAY, DARK_GRAY, text_color=BLACK, font=font_small)
                
                man_cost = b["cost"] * 10
                man_text = "Manager Hired!" if b["has_manager"] else f"Hire Manager\nCost: ${man_cost:,.0f}"
                btn_manager = Button(650, y_offset, 200, 80, man_text, GOLD if b["has_manager"] else BLUE, DARK_BLUE, text_color=BLACK, font=font_small)

                if btn_buy.is_clicked(event, scroll_y) and state["money"] >= b["cost"]:
                    state["money"] -= b["cost"]
                    b["owned"] += 1
                    b["cost"] *= 1.15
                    if b["owned"] in [25, 50, 100, 200]: b["milestone_mult"] *= 2

                if not b["has_manager"] and btn_manager.is_clicked(event, scroll_y) and state["money"] >= man_cost:
                    state["money"] -= man_cost
                    b["has_manager"] = True

                btn_buy.draw(screen, scroll_y)
                btn_manager.draw(screen, scroll_y)
                y_offset += 100

        # --- TAB: MARKETS & BANK ---
        elif current_tab == "Markets":
            # Bank UI
            btn_deposit = Button(200, 200, 300, 80, f"Deposit 25% Cash\nBank: ${state['bank_balance']:,.2f}", DARK_GREEN, GREEN)
            btn_withdraw = Button(550, 200, 300, 80, "Withdraw All", RED, (200, 50, 50))
            
            if btn_deposit.is_clicked(event, scroll_y) and state["money"] > 0:
                amount = state["money"] * 0.25
                state["money"] -= amount
                state["bank_balance"] += amount
            if btn_withdraw.is_clicked(event, scroll_y):
                state["money"] += state["bank_balance"]
                state["bank_balance"] = 0

            btn_deposit.draw(screen, scroll_y)
            btn_withdraw.draw(screen, scroll_y)
            screen.blit(font_medium.render("Bank earns 2% interest every 5 seconds.", True, BLACK), (200, 160 + scroll_y))

            # Markets UI
            y_offset = 350
            for name, s in state["markets"].items():
                b_buy = Button(200, y_offset, 250, 60, f"BUY {name}\n${s['price']:,.0f}", DARK_BLUE, BLUE, font=font_small)
                b_sell = Button(500, y_offset, 250, 60, f"SELL {name}\nOwn: {s['owned']}", DARK_GREEN, GREEN, font=font_small)
                
                if b_buy.is_clicked(event, scroll_y) and state["money"] >= s["price"]:
                    state["money"] -= s["price"]
                    s["owned"] += 1
                if b_sell.is_clicked(event, scroll_y) and s["owned"] > 0:
                    state["money"] += s["price"]
                    s["owned"] -= 1

                b_buy.draw(screen, scroll_y)
                b_sell.draw(screen, scroll_y)
                y_offset += 80

        # --- TAB: LUXURY ASSETS ---
        elif current_tab == "Luxury":
            y_offset = 180
            for name, lux in state["luxuries"].items():
                if lux["owned"] == 0: # Only show unowned items to save space
                    btn_buy = Button(WIDTH//2 - 250, y_offset, 500, 60, f"Buy {name}\nCost: ${lux['cost']:,.0f} | Boost: +{lux['boost']*100:.0f}%", GOLD, (200, 180, 0), text_color=BLACK, font=font_small)
                    if btn_buy.is_clicked(event, scroll_y) and state["money"] >= lux["cost"]:
                        state["money"] -= lux["cost"]
                        lux["owned"] = 1
                    btn_buy.draw(screen, scroll_y)
                    y_offset += 80

    # --- Render Global UI (Stays on top of scrolling) ---
    pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, 140))
    
    # News Ticker
    news_x -= 3
    if news_x < -800:
        news_x = WIDTH
        current_news = random.choice(news_headlines)
    screen.blit(font_medium.render(current_news, True, GOLD), (news_x, 10))

    # Stats
    screen.blit(font_large.render(f"Cash: ${state['money']:,.2f}", True, GREEN), (20, 50))
    screen.blit(font_small.render(f"Net Income: ${current_income:,.2f} / sec (Taxes Deduced)", True, WHITE), (20, 100))
    
    lux_mult = (get_luxury_multiplier() - 1) * 100
    prestige_text = f"Prestige: {state['prestige_multiplier']:.2f}x | Luxury Boost: +{lux_mult:.0f}%"
    screen.blit(font_small.render(prestige_text, True, CYAN), (WIDTH - 400, 50))

    # Draw Tabs
    for btn in tab_buttons:
        btn.draw(screen)

    # Particles
    for p in reversed(particles):
        p.update_and_draw(screen)
        if p.alpha <= 0:
            particles.remove(p)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
