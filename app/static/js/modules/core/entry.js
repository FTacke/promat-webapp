/**
 * Core Entry Point
 * Loaded on every page via base.html.
 */

import { initCsrfProtection } from "./csrf.js";
import { initAuthHandler, checkAutoLogin } from "./auth_handler.js";
import { initPageRouter } from "./router.js";
import { initPreloadGuard, initPageTitleAndScroll } from "./ui.js";
import { initConfig } from "./config.js";
import { initFlashSnackbar } from "./snackbar.js";
import { initExternalHttpLinks } from "./external-links.js";
import { initAdmonitions } from "./admonitions.js";

// Import legacy main.js to preserve existing functionality (Navigation, Token Refresh, etc.)
import "../../main.js";

function initDatawrapperEmbedsWhenPresent() {
    if (!document.querySelector('iframe[data-provider="datawrapper"]')) {
        return;
    }

    void import("./datawrapper.js").then(({ initDatawrapperEmbeds }) => {
        initDatawrapperEmbeds();
    });
}

function initTeachingCitationCopyWhenPresent() {
    if (!document.querySelector("[data-copy-text]")) {
        return;
    }

    void import("./teaching-citation-copy.js").then(({ initTeachingCitationCopy }) => {
        initTeachingCitationCopy();
    });
}

function initTeachingMiniPlayersWhenPresent() {
    if (!document.querySelector("[data-teaching-mini-player]")) {
        return;
    }

    void import("./teaching-mini-player.js").then(({ initTeachingMiniPlayers }) => {
        initTeachingMiniPlayers();
    });
}

// Initialize Config
initConfig();

// Initialize CSRF protection immediately (it attaches event listeners)
initCsrfProtection();

// Check for auto-login immediately (mimicking the IIFE at end of body)
checkAutoLogin();

// Initialize Preload Guard immediately
initPreloadGuard();

// Initialize Page Title and Scroll logic
initPageTitleAndScroll();

// Initialize Flash Snackbar (shows success messages from login etc.)
initFlashSnackbar();

// Ensure external links open in a separate tab/window across the app.
initExternalHttpLinks();

// Register one shared listener for responsive Datawrapper embeds.
initDatawrapperEmbedsWhenPresent();

// Enable compact public mini-players on Teaching pages when present.
initTeachingMiniPlayersWhenPresent();
initTeachingCitationCopyWhenPresent();

document.addEventListener('DOMContentLoaded', () => {
    // Initialize Auth Handler (401 listener and param check)
    initAuthHandler();

    // Initialize shared admonition toggles
    initAdmonitions();
    
    // Initialize Page Router
    initPageRouter();
});

document.addEventListener("turbo:load", () => {
    initAdmonitions();
    initDatawrapperEmbedsWhenPresent();
    initTeachingCitationCopyWhenPresent();
    initTeachingMiniPlayersWhenPresent();
});
