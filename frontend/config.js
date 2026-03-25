/**
 * @author Eidan Khan
 */
const isLocal = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1";

const CONFIG = {
    // Automatically switches based on where the browser is running
    API_BASE_URL: isLocal 
        ? "http://localhost/api" 
        : "https://api.transcripto.dev",
    
    VERSION: "1.0.0"
};