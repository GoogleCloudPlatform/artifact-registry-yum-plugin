//  Copyright 2022 Google LLC
//
//  Licensed under the Apache License, Version 2.0 (the "License");
//  you may not use this file except in compliance with the License.
//  You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
//  Unless required by applicable law or agreed to in writing, software
//  distributed under the License is distributed on an "AS IS" BASIS,
//  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//  See the License for the specific language governing permissions and
//  limitations under the License.

package main

import (
	"context"
	"flag"
	"fmt"
	"os"

	"golang.org/x/oauth2"
	"golang.org/x/oauth2/google"
)

const (
	cloudPlatformScope = "https://www.googleapis.com/auth/cloud-platform"
)

var (
	serviceAccountEmail = flag.String("service_account_email", "",
		"Email of a service account to use on Google Compute Engine")
	serviceAccountJSON = flag.String("service_account_json", "", "Path to a service account key in JSON format")
)

func main() {
	flag.Parse()
	ctx := context.Background()
	token, err := getToken(ctx)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Failed to get token with error: %v\n", err)
		os.Exit(1)
	}

	fmt.Print(token)
}

func debug(msg string) {
	fmt.Fprintf(os.Stderr, "DEBUG: %s\n", msg)
}

func getToken(ctx context.Context) (string, error) {
	var ts oauth2.TokenSource
	switch {
	case *serviceAccountJSON != "":
		debug("Obtain credentials using service account JSON")
		json, err := os.ReadFile(*serviceAccountJSON)
		if err != nil {
			return "", fmt.Errorf("unable to read service account JSON file: %v", err)
		}

		creds, err := google.CredentialsFromJSON(ctx, json, cloudPlatformScope)
		if err != nil {
			return "", fmt.Errorf("unable to obtain creds from service account JSON: %v", err)
		}

		ts = creds.TokenSource

	case *serviceAccountEmail != "":
		debug("Obtain credentials using specific service account email attached to VM")
		ts = google.ComputeTokenSource(*serviceAccountEmail)

	default:
		debug("Obtain credentials using default lookup path")
		creds, err := google.FindDefaultCredentials(ctx)
		if err != nil {
			return "", fmt.Errorf("unable to find default creds: %v", err)
		}

		ts = creds.TokenSource
	}

	if ts == nil {
		return "", fmt.Errorf("got nil token source")
	}

	token, err := ts.Token()
	if err != nil {
		return "", fmt.Errorf("unable to obtain token from token source: %v", err)
	}

	debug("Got a token")

	return token.AccessToken, nil
}
