import { createBrowserRouter } from "react-router";
import { Landing } from "./pages/Landing";
import { Preferences } from "./pages/Preferences";
import { Discover } from "./pages/Discover";
import { Playlist } from "./pages/Playlist";

export const router = createBrowserRouter([
  {
    path: "/",
    Component: Landing,
  },
  {
    path: "/preferences",
    Component: Preferences,
  },
  {
    path: "/discover",
    Component: Discover,
  },
  {
    path: "/playlist",
    Component: Playlist,
  },
]);
