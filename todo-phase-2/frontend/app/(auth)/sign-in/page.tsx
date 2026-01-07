import Link from "next/link";
import { SignInForm } from "@/components/auth/sign-in-form";

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
      <SignInForm />
    </>
  );
}
