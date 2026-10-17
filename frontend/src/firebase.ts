import { initializeApp, getApps, getApp } from "firebase/app";
import { getAnalytics, isSupported, Analytics } from "firebase/analytics";
import { getAuth } from "firebase/auth";
import { getFirestore } from "firebase/firestore";

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY || "AIzaSyAQw9LVUcfmF1rS9UA6PDapBkF6T0yWDYU",
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN || "tantra-58717.firebaseapp.com",
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID || "tantra-58717",
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET || "tantra-58717.firebasestorage.app",
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID || "582210694317",
  appId: import.meta.env.VITE_FIREBASE_APP_ID || "1:582210694317:web:a97ae084638960df6aea24",
  measurementId: import.meta.env.VITE_FIREBASE_MEASUREMENT_ID || "G-KMN58MFTKF"
};

// Initialize Firebase (avoids re-initialization during HMR or multiple imports)
export const app = getApps().length === 0 ? initializeApp(firebaseConfig) : getApp();

// Export Firebase services for modular consumption
export const auth = getAuth(app);
export const db = getFirestore(app);

// Safe Analytics initialization (only runs when supported in the browser environment)
let analytics: Analytics | null = null;
if (typeof window !== "undefined") {
  isSupported()
    .then((supported) => {
      if (supported) {
        analytics = getAnalytics(app);
      }
    })
    .catch(() => {
      // Gracefully ignore environments where analytics is blocked or unsupported
    });
}

export { analytics };
export default app;
