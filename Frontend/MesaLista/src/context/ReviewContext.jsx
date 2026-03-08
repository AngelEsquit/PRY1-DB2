import { createContext, useContext, useState } from "react";
import { reviews as initialReviews } from "../data/mockData";

const ReviewContext = createContext();

export function ReviewProvider({ children }) {
  const [reviews, setReviews] = useState(initialReviews);

  const addReview = (newReview) => {
    setReviews((prev) => [
      {
        id: Date.now(),
        ...newReview,
      },
      ...prev,
    ]);
  };

  return (
    <ReviewContext.Provider value={{ reviews, addReview }}>
      {children}
    </ReviewContext.Provider>
  );
}

export function useReviews() {
  return useContext(ReviewContext);
}