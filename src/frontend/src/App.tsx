import "@xyflow/react/dist/style.css";
import { Suspense } from "react";
import { RouterProvider } from "react-router-dom";
import { Provider } from "./components/ui/provider";
import { LoadingPage } from "./pages/LoadingPage";
import router from "./routes";

export default function App() {
  return (
    <Suspense fallback={<LoadingPage />}>
      <Provider>
        <RouterProvider router={router} />
      </Provider>
    </Suspense>
  );
}
