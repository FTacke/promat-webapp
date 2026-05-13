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
import { initDatawrapperEmbeds } from "./datawrapper.js";
import { initTeachingCitationCopy } from "./teaching-citation-copy.js";
import { initTeachingMiniPlayers } from "./teaching-mini-player.js";

// Import legacy main.js to preserve existing functionality (Navigation, Token Refresh, etc.)
import "../../main.js";

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
initDatawrapperEmbeds();

// Enable compact public mini-players on Teaching pages when present.
initTeachingMiniPlayers();
initTeachingCitationCopy();

document.addEventListener('DOMContentLoaded', () => {
    // Initialize Auth Handler (401 listener and param check)
    initAuthHandler();

    // Initialize shared admonition toggles
    initAdmonitions();
    initTeachingCitationCopy();
    
    // Initialize Page Router
    initPageRouter();

    initTeachingMiniPlayers();
});

document.addEventListener("turbo:load", () => {
    initAdmonitions();
    initTeachingCitationCopy();
    initTeachingMiniPlayers();
});
