import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import { DesignSystemProvider } from "../providers/DesignSystemProvider";
import "../styles/index.css";

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <DesignSystemProvider>
      <App />
    </DesignSystemProvider>
  </React.StrictMode>,
);
