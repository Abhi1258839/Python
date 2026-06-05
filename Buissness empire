import pygame
import sys
import json
import os
import time
import random
import math

# --- Initialization ---
pygame.init()
WIDTH, HEIGHT = 1100, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Advanced Business Empire")

# Colors
WHITE, BLACK = (245, 245, 250), (20, 20, 20)
GREEN, DARK_GREEN = (76, 175, 80), (56, 142, 60)
BLUE, DARK_BLUE = (33, 150, 243), (25, 118, 210)
GRAY, DARK_GRAY = (200, 200, 200), (150, 150, 150)
GOLD = (255, 215, 0)
RED = (244, 67, 54)
PURPLE = (156, 39, 176)

# Fonts
font_large = pygame.font.SysFont("arial", 48, bold=True)
font_medium = pygame.font.SysFont("arial", 24, bold=True)
font_small = pygame.font.SysFont("arial", 16)

# --- Game State ---
SAVE_FILE = "empire_save.json"

# Default state
state = {
    "money": 0.0,
    "lifetime_money": 0.0,
    "click_value": 1.0,
    "click_upgrade_cost": 20.0,
    "prestige_multiplier": 1.0,
    "last_played": time.time(),
    "manager_bonus": 1.0,
    "manager_cost": 10000.0,
    "businesses": {
        "Lemonade Stand": {"cost": 50, "base_income": 2, "owned": 0, "milestone_mult": 1},
        "Tech Startup": {"cost": 500, "base_income": 25, "owned": 0, "milestone_mult": 1},
        "Real Estate": {"cost": 5000, "base_income": 300, "owned": 0, "milestone_mult": 1},
        "Bank": {"cost": 50000, "base_income": 4000, "owned": 0, "milestone_mult": 1}
    },
    "stocks": {
        "TechCorp": {"price": 100.0, "owned": 0, "volatility": 0.1},
        "GoldMines": {"price": 500.0, "owned": 0, "volatility": 0.05}
    }
}

# Load Game
if os.path.exists(SAVE_FILE):
    try:
        with open(SAVE_FILE, "r") as f:
            loaded_state = json.load(f)
            # Update default state with loaded data to prevent crashing on new updates
            for key in loaded_state:
                if key in state and isinstance(state[key], dict):
                    state[key].update(loaded_state[key])
                else:
                    state[key] = loaded_state[key]
    except Exception as e:
        print("Save file corrupted, starting fresh.")

def save_game():
    state["last_played"] = time.time()
    with open(SAVE_FILE, "w") as f:
        json.dump(state, f)

# --- Helper Classes ---
class Particle:
    def __init__(self, x, y, text, color):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.alpha = 255
        self.surf = font_medium.render(self.text, True, self.color).convert_alpha()

    def update_and_draw(self, surface):
        self.y -= 2 # Float up
        self.alpha -= 5 # Fade out
        self.surf.set_alpha(max(0, self.alpha))
        surface.blit(self.surf, (self.x, self.y))

class Button:
    def __init__(self, x, y, w, h, text, color, hover_color, text_color=WHITE, font=font_medium):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color, self.hover_color = color, hover_color
        self.text_color, self.font = text_color, font

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        current_color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.color
        pygame.draw.rect(surface, current_color, self.rect, border_radius=8)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=8)
        
        # Handle multi-line text (separated by '\n')
        lines = self.text.split('\n')
        for i, line in enumerate(lines):
            text_surf = self.font.render(line, True, self.text_color)
            text_rect = text_surf.get_rect(center=(self.rect.centerx, self.rect.y + (self.rect.height / (len(lines)+1)) * (i+1)))
            surface.blit(text_surf, text_rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(event.pos)
        return False

# --- Core Mechanics Functions ---
def get_idle_income():
    income = 0
    for biz in state["businesses"].values():
        biz_income = biz["base_income"] * biz["owned"] * biz["milestone_mult"]
        income += biz_income
    return income * state["prestige_multiplier"] * state["manager_bonus"]

def add_money(amount):
    state["money"] += amount
    state["lifetime_money"] += amount

def check_milestones(biz):
    # Milestones double income at 25, 50, 100, 200
    if biz["owned"] in [25, 50, 100, 200]:
        biz["milestone_mult"] *= 2

def get_prestige_gain():
    # Formula: Square root of lifetime money scaled down
    return max(0, math.floor(math.sqrt(state["lifetime_money"] / 50000)))

# --- Offline Progress Calculation ---
time_away = time.time() - state["last_played"]
if time_away > 60: # If away for more than 1 minute
    offline_earnings = get_idle_income() * time_away
    add_money(offline_earnings)
    print(f"Earned ${offline_earnings:,.2f} while offline for {int(time_away)} seconds!")

# --- Events & Timers ---
IDLE_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(IDLE_EVENT, 1000)

STOCK_EVENT = pygame.USEREVENT + 2
pygame.time.set_timer(STOCK_EVENT, 3000) # Stocks change every 3 seconds

SAVE_EVENT = pygame.USEREVENT + 3
pygame.time.set_timer(SAVE_EVENT, 10000) # Autosave every 10 seconds

# Variables for Game Loop
particles = []
clock = pygame.time.Clock()
running = True

# Golden Event Variables
golden_active = False
golden_timer = 0
golden_rect = pygame.Rect(0, 0, 80, 80)

# --- Main Game Loop ---
while running:
    screen.fill(WHITE)
    mouse_pos = pygame.mouse.get_pos()
    current_income = get_idle_income()
    click_power = state["click_value"] * state["prestige_multiplier"]

    # 1. Handle Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_game()
            running = False

        if event.type == IDLE_EVENT:
            add_money(current_income)
            
            # 5% chance to spawn a Golden Event every second if not active
            if not golden_active and random.random() < 0.05:
                golden_active = True
                golden_timer = 5000 # Lasts 5 seconds
                golden_rect.x = random.randint(50, WIDTH - 150)
                golden_rect.y = random.randint(150, HEIGHT - 150)

        if event.type == STOCK_EVENT:
            for s in state["stocks"].values():
                change = random.uniform(-s["volatility"], s["volatility"])
                s["price"] = max(1.0, s["price"] * (1 + change)) # Price can't drop below 1

        if event.type == SAVE_EVENT:
            save_game()

        # --- Interactivity ---
        # Main Click
        btn_main_click = Button(20, 150, 300, 150, f"CLICK\n(+${click_power:,.2f})", GREEN, DARK_GREEN)
        if btn_main_click.is_clicked(event):
            add_money(click_power)
            particles.append(Particle(mouse_pos[0], mouse_pos[1] - 20, f"+${click_power:,.1f}", DARK_GREEN))

        # Click Upgrade
        btn_upg_click = Button(20, 320, 300, 60, f"Upgrade Click\nCost: ${state['click_upgrade_cost']:,.0f}", BLUE, DARK_BLUE, font=font_small)
        if btn_upg_click.is_clicked(event) and state["money"] >= state["click_upgrade_cost"]:
            state["money"] -= state["click_upgrade_cost"]
            state["click_value"] *= 2
            state["click_upgrade_cost"] *= 2.2

        # Manager Upgrade (Global 1.5x Multiplier)
        btn_manager = Button(20, 400, 300, 60, f"Hire Manager (1.5x Income)\nCost: ${state['manager_cost']:,.0f}", PURPLE, (120, 30, 140), font=font_small)
        if btn_manager.is_clicked(event) and state["money"] >= state["manager_cost"]:
            state["money"] -= state["manager_cost"]
            state["manager_bonus"] *= 1.5
            state["manager_cost"] *= 5

        # Prestige
        prestige_gain = get_prestige_gain()
        btn_prestige = Button(20, 580, 300, 80, f"SELL EMPIRE (PRESTIGE)\nGain +{prestige_gain}% Global Bonus", RED, (200, 50, 50), font=font_small)
        if btn_prestige.is_clicked(event) and prestige_gain > 0:
            # Reset logic
            state["prestige_multiplier"] += (prestige_gain / 100.0)
            state["money"] = 0
            state["click_value"] = 1
            state["click_upgrade_cost"] = 20
            state["manager_bonus"] = 1.0
            state["manager_cost"] = 10000.0
            for b in state["businesses"].values():
                b["owned"] = 0
                b["milestone_mult"] = 1
                b["cost"] = [50, 500, 5000, 50000][list(state["businesses"].keys()).index(list(state["businesses"].keys())[list(state["businesses"].values()).index(b)])] # Reset costs cleanly

        # Businesses Purchase
        y_offset = 150
        business_buttons = {}
        for name, b in state["businesses"].items():
            btn = Button(350, y_offset, 350, 80, f"{name} (Own: {b['owned']})\nCost: ${b['cost']:,.0f} | +${b['base_income']*b['milestone_mult']:,.0f}/s", GRAY, DARK_GRAY, text_color=BLACK, font=font_small)
            business_buttons[name] = btn
            if btn.is_clicked(event) and state["money"] >= b["cost"]:
                state["money"] -= b["cost"]
                b["owned"] += 1
                b["cost"] *= 1.15 # 15% compound scaling
                check_milestones(b)
            y_offset += 100

        # Stocks Purchase / Sell
        y_offset = 150
        stock_buttons_buy, stock_buttons_sell = {}, {}
        for name, s in state["stocks"].items():
            b_buy = Button(730, y_offset, 160, 60, f"BUY {name}\n${s['price']:,.0f}", DARK_BLUE, BLUE, font=font_small)
            b_sell = Button(900, y_offset, 160, 60, f"SELL {name}\nOwn: {s['owned']}", DARK_GREEN, GREEN, font=font_small)
            
            if b_buy.is_clicked(event) and state["money"] >= s["price"]:
                state["money"] -= s["price"]
                s["owned"] += 1
            if b_sell.is_clicked(event) and s["owned"] > 0:
                state["money"] += s["price"]
                s["owned"] -= 1

            stock_buttons_buy[name] = b_buy
            stock_buttons_sell[name] = b_sell
            y_offset += 80

        # Golden Event Click
        if golden_active and event.type == pygame.MOUSEBUTTONDOWN:
            if golden_rect.collidepoint(event.pos):
                bonus = current_income * 120 # 2 minutes worth of income instantly
                add_money(bonus)
                particles.append(Particle(mouse_pos[0], mouse_pos[1], f"MARKET BOOM! +${bonus:,.0f}", GOLD))
                golden_active = False

    # 2. Rendering
    # Header UI
    pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, 120))
    screen.blit(font_large.render(f"Bank: ${state['money']:,.2f}", True, GREEN), (20, 10))
    screen.blit(font_medium.render(f"Income: ${current_income:,.2f} / sec", True, WHITE), (20, 70))
    
    prestige_text = f"Prestige Multiplier: {state['prestige_multiplier']:.2f}x | Lifetime Cash: ${state['lifetime_money']:,.0f}"
    screen.blit(font_small.render(prestige_text, True, GOLD), (WIDTH - 500, 20))
    screen.blit(font_small.render("Stock Market", True, WHITE), (830, 90))

    # Draw UI Elements
    btn_main_click.draw(screen)
    btn_upg_click.draw(screen)
    btn_manager.draw(screen)
    btn_prestige.draw(screen)

    for btn in business_buttons.values(): btn.draw(screen)
    for btn in stock_buttons_buy.values(): btn.draw(screen)
    for btn in stock_buttons_sell.values(): btn.draw(screen)

    # Draw Golden Event
    if golden_active:
        golden_timer -= clock.get_time()
        if golden_timer <= 0:
            golden_active = False
        else:
            pygame.draw.circle(screen, GOLD, golden_rect.center, 40)
            screen.blit(font_small.render("CLICK!", True, BLACK), (golden_rect.x + 15, golden_rect.y + 30))

    # Update and Draw Particles
    for p in reversed(particles):
        p.update_and_draw(screen)
        if p.alpha <= 0:
            particles.remove(p)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
