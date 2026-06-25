# Security Notes

For a public hosted service, add these controls before allowing untrusted uploads:

1. Maximum request body size.
2. PNG/JPEG signature validation.
3. Image dimension limits.
4. Re-encode uploaded images before storing.
5. Store files outside the application source tree.
6. Use random object names.
7. Run Android APK builds inside disposable containers.
8. Apply CPU, memory, disk, and network limits for workers.
9. Do not bundle official app assets, logos, character images, or guide PDFs.
