import { Routes, Route } from "react-router-dom";
import { Header } from "@/components/layout/header";

import HomePage from "@/app/HomePage";
import LoginPage from "@/app/auth/LoginPage";
import RegisterPage from "@/app/auth/RegisterPage";
import BrowseNovelsPage from "@/app/novels/BrowseNovelsPage";
import NovelDetailPage from "@/app/novels/NovelDetailPage";
import ChapterReaderPage from "@/app/novels/ChapterReaderPage";
import ProfilePage from "@/app/ProfilePage";
import LibraryPage from "@/app/LibraryPage";
import SearchPage from "@/app/SearchPage";
import PurchaseHistoryPage from "@/app/PurchaseHistoryPage";
import AuthorDashboardPage from "@/app/author/AuthorDashboardPage";
import NewNovelPage from "@/app/author/NewNovelPage";
import EditNovelPage from "@/app/author/EditNovelPage";
import NewChapterPage from "@/app/author/NewChapterPage";
import EditChapterPage from "@/app/author/EditChapterPage";
import AuthorProfilePage from "@/app/authors/AuthorProfilePage";
import NotFoundPage from "@/app/NotFoundPage";

export default function App() {
  return (
    <>
      <Header />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />

        <Route path="/novels" element={<BrowseNovelsPage />} />
        <Route path="/novels/:slug" element={<NovelDetailPage />} />
        <Route path="/novels/:slug/chapters/:number" element={<ChapterReaderPage />} />

        <Route path="/profile" element={<ProfilePage />} />
        <Route path="/library" element={<LibraryPage />} />
        <Route path="/search" element={<SearchPage />} />
        <Route path="/payments/history" element={<PurchaseHistoryPage />} />

        <Route path="/author/dashboard" element={<AuthorDashboardPage />} />
        <Route path="/author/novels/new" element={<NewNovelPage />} />
        <Route path="/author/novels/:novelId/edit" element={<EditNovelPage />} />
        <Route path="/author/novels/:novelId/chapters/new" element={<NewChapterPage />} />
        <Route
          path="/author/novels/:novelId/chapters/:chapterId/edit"
          element={<EditChapterPage />}
        />

        <Route path="/authors/:username" element={<AuthorProfilePage />} />

        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </>
  );
}
