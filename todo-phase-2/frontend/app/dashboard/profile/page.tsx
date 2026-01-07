"use client";

import { useState } from "react";
import { useSession } from "@/lib/auth-client";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export default function ProfilePage() {
  const { data: session } = useSession();
  const [isEditing, setIsEditing] = useState(false);
  const [name, setName] = useState(session?.user?.name || "");

  const userName = session?.user?.name || session?.user?.email?.split("@")[0] || "User";
  const userEmail = session?.user?.email || "";
  const userInitial = userName.charAt(0).toUpperCase();
  const createdAt = session?.user?.createdAt
    ? new Date(session.user.createdAt).toLocaleDateString("en-US", {
        year: "numeric",
        month: "long",
        day: "numeric",
      })
    : "Unknown";

  const handleSave = async () => {
    // TODO: Implement profile update API call
    setIsEditing(false);
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Profile</h1>
        <p className="text-sm text-gray-500 mt-1">Manage your account information</p>
      </div>

      {/* Profile Card */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="flex h-16 w-16 items-center justify-center rounded-full bg-gradient-to-br from-blue-600 to-indigo-600 text-2xl font-bold text-white">
                {userInitial}
              </div>
              <div>
                <h2 className="text-xl font-semibold text-gray-900">{userName}</h2>
                <p className="text-sm text-gray-500">{userEmail}</p>
              </div>
            </div>
            {!isEditing && (
              <Button variant="outline" onClick={() => setIsEditing(true)}>
                <svg className="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                </svg>
                Edit Profile
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            {/* Profile Form */}
            <div className="grid gap-6 sm:grid-cols-2">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Full Name
                </label>
                {isEditing ? (
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                    placeholder="Enter your name"
                  />
                ) : (
                  <p className="rounded-lg bg-gray-50 px-4 py-2.5 text-sm text-gray-900">
                    {userName}
                  </p>
                )}
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Email Address
                </label>
                <p className="rounded-lg bg-gray-50 px-4 py-2.5 text-sm text-gray-900">
                  {userEmail}
                </p>
              </div>
            </div>

            {/* Actions */}
            {isEditing && (
              <div className="flex items-center gap-3 pt-4 border-t border-gray-100">
                <Button onClick={handleSave}>Save Changes</Button>
                <Button variant="outline" onClick={() => setIsEditing(false)}>
                  Cancel
                </Button>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Account Information */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <div className="rounded-lg bg-purple-100 p-2">
              <svg className="h-5 w-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">Account Information</h3>
              <p className="text-xs text-gray-500">Details about your account</p>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <div className="rounded-lg border border-gray-100 bg-gray-50 p-4">
              <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">Member Since</p>
              <p className="mt-1 text-sm font-semibold text-gray-900">{createdAt}</p>
            </div>
            <div className="rounded-lg border border-gray-100 bg-gray-50 p-4">
              <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">Plan</p>
              <p className="mt-1 text-sm font-semibold text-gray-900">Free Plan</p>
            </div>
            <div className="rounded-lg border border-gray-100 bg-gray-50 p-4">
              <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">Status</p>
              <div className="mt-1 flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-green-500"></span>
                <p className="text-sm font-semibold text-gray-900">Active</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Danger Zone */}
      <Card className="border-red-200">
        <CardHeader>
          <div className="flex items-center gap-2">
            <div className="rounded-lg bg-red-100 p-2">
              <svg className="h-5 w-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <div>
              <h3 className="font-semibold text-red-900">Danger Zone</h3>
              <p className="text-xs text-red-600">Irreversible account actions</p>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 p-4 rounded-lg border border-red-100 bg-red-50">
            <div>
              <p className="text-sm font-medium text-red-900">Delete Account</p>
              <p className="text-xs text-red-600 mt-1">Permanently delete your account and all data</p>
            </div>
            <Button variant="destructive" className="shrink-0">
              Delete Account
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
