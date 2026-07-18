import * as React from "react";
import { useRequireAuth } from "@/hooks/use-require-auth";
import { useAuthStore } from "@/store/authStore";
import { updateProfile, uploadAvatar, changePassword } from "@/lib/user-api";
import { extractErrorMessage } from "@/lib/api";
import { getMediaUrl } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Alert } from "@/components/ui/alert";

export default function ProfilePage() {
  const { user, isReady } = useRequireAuth();
  const setUser = useAuthStore((s) => s.setUser);

  const [displayName, setDisplayName] = React.useState("");
  const [bio, setBio] = React.useState("");
  const [profileError, setProfileError] = React.useState<string | null>(null);
  const [profileSuccess, setProfileSuccess] = React.useState(false);
  const [isSavingProfile, setIsSavingProfile] = React.useState(false);
  const [isUploadingAvatar, setIsUploadingAvatar] = React.useState(false);

  const [currentPassword, setCurrentPassword] = React.useState("");
  const [newPassword, setNewPassword] = React.useState("");
  const [passwordError, setPasswordError] = React.useState<string | null>(null);
  const [passwordSuccess, setPasswordSuccess] = React.useState(false);
  const [isSavingPassword, setIsSavingPassword] = React.useState(false);

  React.useEffect(() => {
    if (user) {
      setDisplayName(user.display_name);
      setBio(user.bio ?? "");
    }
  }, [user]);

  if (!isReady || !user) {
    return <p className="mx-auto max-w-xl px-6 py-10 font-body text-sm text-slate-light">Loading…</p>;
  }

  async function handleSaveProfile(e: React.FormEvent) {
    e.preventDefault();
    setProfileError(null);
    setProfileSuccess(false);
    setIsSavingProfile(true);
    try {
      const updated = await updateProfile({ display_name: displayName, bio });
      setUser(updated);
      setProfileSuccess(true);
    } catch (err) {
      setProfileError(extractErrorMessage(err));
    } finally {
      setIsSavingProfile(false);
    }
  }

  async function handleAvatarChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setIsUploadingAvatar(true);
    setProfileError(null);
    try {
      const updated = await uploadAvatar(file);
      setUser(updated);
    } catch (err) {
      setProfileError(extractErrorMessage(err));
    } finally {
      setIsUploadingAvatar(false);
      e.target.value = "";
    }
  }

  async function handleChangePassword(e: React.FormEvent) {
    e.preventDefault();
    setPasswordError(null);
    setPasswordSuccess(false);
    setIsSavingPassword(true);
    try {
      await changePassword({ current_password: currentPassword, new_password: newPassword });
      setPasswordSuccess(true);
      setCurrentPassword("");
      setNewPassword("");
    } catch (err) {
      setPasswordError(extractErrorMessage(err));
    } finally {
      setIsSavingPassword(false);
    }
  }

  const avatarUrl = getMediaUrl(user.avatar);

  return (
    <main className="mx-auto max-w-xl px-6 py-10">
      <h1 className="mb-8 font-display text-3xl font-medium text-parchment">Your profile</h1>

      <section className="mb-10 flex items-center gap-4">
        <div className="relative h-20 w-20 shrink-0 overflow-hidden rounded-full bg-ink-soft">
          {avatarUrl ? (
            <img src={avatarUrl} alt={user.display_name} className="h-full w-full object-cover" />
          ) : (
            <div className="flex h-full w-full items-center justify-center font-display text-xl text-slate-light">
              {user.display_name.charAt(0).toUpperCase()}
            </div>
          )}
        </div>
        <div>
          <Label htmlFor="avatar" className="mb-1">
            Avatar
          </Label>
          <input
            id="avatar"
            type="file"
            accept="image/jpeg,image/png,image/webp,image/gif"
            onChange={handleAvatarChange}
            disabled={isUploadingAvatar}
            className="font-body text-xs text-slate-light file:mr-3 file:rounded file:border-0 file:bg-ink-soft file:px-3 file:py-1.5 file:text-parchment"
          />
        </div>
      </section>

      <form onSubmit={handleSaveProfile} className="mb-12 flex flex-col gap-4">
        <h2 className="font-display text-lg font-medium text-parchment">Details</h2>
        {profileError && <Alert variant="error">{profileError}</Alert>}
        {profileSuccess && <Alert variant="success">Profile updated.</Alert>}

        <div>
          <Label htmlFor="displayName">Display name</Label>
          <Input
            id="displayName"
            required
            value={displayName}
            onChange={(e) => setDisplayName(e.target.value)}
          />
        </div>

        <div>
          <Label htmlFor="bio">Bio</Label>
          <Textarea
            id="bio"
            rows={4}
            maxLength={2000}
            value={bio}
            onChange={(e) => setBio(e.target.value)}
          />
        </div>

        <Button type="submit" isLoading={isSavingProfile} className="self-start">
          Save changes
        </Button>
      </form>

      <form onSubmit={handleChangePassword} className="flex flex-col gap-4">
        <h2 className="font-display text-lg font-medium text-parchment">Change password</h2>
        {passwordError && <Alert variant="error">{passwordError}</Alert>}
        {passwordSuccess && <Alert variant="success">Password changed.</Alert>}

        <div>
          <Label htmlFor="currentPassword">Current password</Label>
          <Input
            id="currentPassword"
            type="password"
            autoComplete="current-password"
            required
            value={currentPassword}
            onChange={(e) => setCurrentPassword(e.target.value)}
          />
        </div>

        <div>
          <Label htmlFor="newPassword">New password</Label>
          <Input
            id="newPassword"
            type="password"
            autoComplete="new-password"
            required
            minLength={8}
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
          />
        </div>

        <Button type="submit" isLoading={isSavingPassword} className="self-start">
          Update password
        </Button>
      </form>
    </main>
  );
}
