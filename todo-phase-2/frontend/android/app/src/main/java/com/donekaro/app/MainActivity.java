package com.donekaro.app;

import android.os.Bundle;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.net.ConnectivityManager;
import android.net.NetworkInfo;
import android.content.Context;

import com.getcapacitor.BridgeActivity;
import com.codetrixstudio.capacitor.GoogleAuth.GoogleAuth;

public class MainActivity extends BridgeActivity {
    private static final String OFFLINE_PAGE = "file:///android_asset/public/offline.html";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        registerPlugin(GoogleAuth.class);
        super.onCreate(savedInstanceState);
        // Note: Notification channels are created in MainApplication.onCreate()
        // to ensure they exist before any FCM messages arrive

        // Set up custom WebView error handling for offline support
        setupOfflineHandler();
    }

    private void setupOfflineHandler() {
        WebView webView = getBridge().getWebView();
        if (webView != null) {
            webView.setWebViewClient(new WebViewClient() {
                @Override
                public void onReceivedError(WebView view, WebResourceRequest request, WebResourceError error) {
                    // Only handle main frame errors
                    if (request.isForMainFrame()) {
                        // Check if it's a network-related error
                        int errorCode = error.getErrorCode();
                        if (errorCode == ERROR_HOST_LOOKUP ||
                            errorCode == ERROR_CONNECT ||
                            errorCode == ERROR_TIMEOUT ||
                            errorCode == ERROR_IO ||
                            !isNetworkAvailable()) {
                            // Load our custom offline page
                            view.loadUrl(OFFLINE_PAGE);
                            return;
                        }
                    }
                    super.onReceivedError(view, request, error);
                }

                @Override
                @SuppressWarnings("deprecation")
                public void onReceivedError(WebView view, int errorCode, String description, String failingUrl) {
                    // Legacy handler for older Android versions
                    if (errorCode == ERROR_HOST_LOOKUP ||
                        errorCode == ERROR_CONNECT ||
                        errorCode == ERROR_TIMEOUT ||
                        errorCode == ERROR_IO ||
                        !isNetworkAvailable()) {
                        view.loadUrl(OFFLINE_PAGE);
                        return;
                    }
                    super.onReceivedError(view, errorCode, description, failingUrl);
                }
            });
        }
    }

    private boolean isNetworkAvailable() {
        ConnectivityManager connectivityManager = (ConnectivityManager) getSystemService(Context.CONNECTIVITY_SERVICE);
        if (connectivityManager != null) {
            NetworkInfo activeNetworkInfo = connectivityManager.getActiveNetworkInfo();
            return activeNetworkInfo != null && activeNetworkInfo.isConnected();
        }
        return false;
    }
}
