BEGIN TRANSACTION;

CREATE TABLE IF NOT EXISTS "Users" (
                                       "UserId" INTEGER NOT NULL PRIMARY KEY,
                                       "Username" TEXT NOT NULL,
                                       "UserInfo" TEXT,
                                       "UserAvatarId" TEXT,
                                       "TelegramUsername" TEXT,
                                       "TelegramFirstName" TEXT,
                                       "TelegramLastName" TEXT,
                                       "TelegramPhoneNumber" TEXT,
                                       "Coins" INTEGER NOT NULL DEFAULT 10000,
                                       "Tickets" INTEGER NOT NULL DEFAULT 5,
                                       "Cups" INTEGER NOT NULL DEFAULT 0,
                                       "Victories" INTEGER NOT NULL DEFAULT 0,
                                       "Defeats" INTEGER NOT NULL DEFAULT 0,
                                       "GamesPlayed" INTEGER NOT NULL DEFAULT 0,
                                       "PenaltyLeft" INTEGER NOT NULL DEFAULT 5,
                                       "PenaltyScored" INTEGER NOT NULL DEFAULT 0,
                                       "ReferralsCount" INTEGER NOT NULL DEFAULT 0,
                                       "ReceivedCoins" INTEGER NOT NULL DEFAULT 0,
                                       "ReceivedTickets" INTEGER NOT NULL DEFAULT 0,
                                       "SmallPacks" INTEGER NOT NULL DEFAULT 0,
                                       "MediumPacks" INTEGER NOT NULL DEFAULT 0,
                                       "BigPacks" INTEGER NOT NULL DEFAULT 0,
                                       "GhostSmallPacks" INTEGER NOT NULL DEFAULT 0,
                                       "GhostMediumPacks" INTEGER NOT NULL DEFAULT 0,
                                       "GhostBigPacks" INTEGER NOT NULL DEFAULT 0,
                                       "IsBanned" INTEGER NOT NULL DEFAULT 0,
                                       "BanEnd" TEXT,
                                       "Warns" INTEGER NOT NULL DEFAULT 0,
                                       "Level" INTEGER NOT NULL DEFAULT 4,
                                       "RegisterDate" TEXT DEFAULT CURRENT_TIMESTAMP,
                                       "Lang" TEXT DEFAULT 'en_US',
                                       "Success" INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS "History" (
                                         "Id" INTEGER PRIMARY KEY AUTOINCREMENT,
                                         "TargetUserId" INTEGER NOT NULL,
                                         "Datetime" TEXT DEFAULT CURRENT_TIMESTAMP,
                                         "ActionType" TEXT,
                                         "Amount" INTEGER,
                                         "LogMessage" TEXT,
                                         FOREIGN KEY ("TargetUserId") REFERENCES "Users"("UserId") ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS "idx_user_success" ON "Users" ("Success" DESC);
CREATE INDEX IF NOT EXISTS "idx_user_cups" ON "Users" ("Cups" DESC);

COMMIT;