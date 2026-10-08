CREATE TABLE users (
user_id         TEXT    PRIMARY KEY,
username        TEXT    NOT NULL,
last_usage_at   DATETIME,
ddos_flags_at   INTEGER NOT NULL CHECK (ddos_flags_at BETWEEN 0 AND 60)
);

CREATE TABLE wishlists (
wishlist_id TEXT PRIMARY KEY,
user_id     TEXT NOT NULL UNIQUE REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE games (
game_id             TEXT    PRIMARY KEY,
game_title          TEXT    NOT NULL,
last_update_date    DATETIME,
last_update_url     TEXT,
last_update_price   NUMERIC CHECK (last_update_price >= 0 AND ROUND(last_update_price, 2) = last_update_price),
last_update_cut     INTEGER CHECK (last_update_cut BETWEEN 0 AND 100),
last_update_voucher TEXT,
last_update_shop    TEXT,
lowest_known_price  NUMERIC CHECK (lowest_known_price >= 0 AND ROUND(lowest_known_price, 2) = lowest_known_price),
lkp_shop            TEXT,
lkp_date            DATETIME
);

CREATE TABLE wishlist_items (
game_id             TEXT    NOT NULL REFERENCES games(game_id) ON DELETE CASCADE,
wishlist_id         TEXT    NOT NULL REFERENCES wishlists(wishlist_id) ON DELETE CASCADE,
alert_rule_type     TEXT    NOT NULL CONSTRAINT chk_type CHECK (alert_rule_type IN ('below', 'observed_low', 'minimum_cut')),
threshold           NUMERIC,
last_notified_price NUMERIC CHECK (last_notified_price >= 0 AND ROUND(last_notified_price, 2) = last_notified_price),
last_notified_at    DATETIME,
last_updated_at     DATETIME,
CHECK (
  (alert_rule_type = 'minimum_cut' AND threshold BETWEEN 0 AND 100) OR
  (alert_rule_type = 'below' AND threshold >= 0) OR
  (alert_rule_type = 'observed_low' AND threshold IS NULL)
),
PRIMARY KEY (game_id, wishlist_id)
);

-- INDEX:
CREATE INDEX idx_wishlist_items_wishlist_id ON wishlist_items(wishlist_id);
CREATE INDEX idx_wishlists_user ON wishlists(user_id);

-- DO NOT FORGET THIS AT STARTUP : PRAGMA foreign_keys = ON;
