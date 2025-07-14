import React from "react";
import { LazyMotion, domAnimation } from "framer-motion";
import TRVForm from "./TRVForm.jsx";

const App = () => {
  return (
    <LazyMotion features={domAnimation}>
      <div className="min-h-screen bg-gray-100 text-gray-900">
        <h1 className="text-center text-2xl font-bold py-6">Team Relative Value Calculator</h1>
        <TRVForm />
      </div>
    </LazyMotion>
  );
};

export default App;