import Link from "next/link";
import { SignInForm } from "@/components/auth/sign-in-form";
import { GoogleSignInButton } from "@/components/auth/google-sign-in-button";

export default function SignInPage() {
  return (
    <>
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900">Sign in to your account</h2>
        <p className="mt-2 text-sm text-gray-600">
          Don&apos;t have an account?{" "}
          <Link
            href="/sign-up"
            className="font-medium text-blue-600 hover:text-blue-500"
          >
            Sign up
          </Link>
        </p>
      </div>

      <div className="mt-6">
        <GoogleSignInButton mode="signin" />
      </div>

      <div className="relative my-6">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t border-gray-200" />
        </div>
        <div className="relative flex justify-center text-sm">
          <span className="bg-white px-4 text-gray-500">or continue with email</span>
        </div>
      </div>

      <SignInForm />
    </>
  );
}
