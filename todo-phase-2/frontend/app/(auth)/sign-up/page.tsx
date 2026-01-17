import Link from "next/link";
import { SignUpForm } from "@/components/auth/sign-up-form";
import { GoogleSignInButton } from "@/components/auth/google-sign-in-button";

export default function SignUpPage() {
  return (
    <>
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900">Create your account</h2>
        <p className="mt-2 text-sm text-gray-600">
          Already have an account?{" "}
          <Link
            href="/sign-in"
            className="font-medium text-blue-600 hover:text-blue-500"
          >
            Sign in
          </Link>
        </p>
      </div>

      <div className="mt-6">
        <GoogleSignInButton mode="signup" />
      </div>

      <div className="relative my-6">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t border-gray-200" />
        </div>
        <div className="relative flex justify-center text-sm">
          <span className="bg-white px-4 text-gray-500">or continue with email</span>
        </div>
      </div>

      <SignUpForm />
    </>
  );
}
