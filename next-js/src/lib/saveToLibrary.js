import { doc, updateDoc, arrayUnion } from "firebase/firestore";
import { db, auth } from "@/lib/firebaseConfig";

async function saveVideoToLibrary(videoUrl) {
  const user = auth.currentUser;
  if (!user) {
    alert("You must be signed in to save videos.");
    return;
  }

  const userRef = doc(db, "users", user.uid);

  try {
    await updateDoc(userRef, {
      library: arrayUnion(videoUrl),
    });
    alert("✅ Video saved to your library!");
  } catch (error) {
    console.error("❌ Error saving video:", error);
    alert("Failed to save video.");
  }
}
