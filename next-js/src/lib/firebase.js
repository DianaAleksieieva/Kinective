// src/lib/firebase.js
import { initializeApp, getApps, getApp } from "firebase/app";
import { getFirestore } from "firebase/firestore";

// Your Firebase config (from Firebase Console -> Project Settings -> SDK setup)
const firebaseConfig = {
  apiKey: "AIzaSyAa1wyUZs5hzwiGsiNs95zTsu052dRB7gU",
  authDomain: "kinective-45347.firebaseapp.com",
  projectId: "kinective-45347",
  storageBucket: "kinective-45347.firebasestorage.app",
  messagingSenderId: "555649577313",
  appId: "1:555649577313:web:eb53db72cea38a19315520",
  measurementId: "G-B8SKBS9ZM5"
};

// Avoid re-initializing on hot reload
const app = !getApps().length ? initializeApp(firebaseConfig) : getApp();

export const db = getFirestore(app);
