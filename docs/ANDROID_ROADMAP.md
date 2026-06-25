# Android APK build roadmap

현재 레포는 Android APK를 직접 빌드하지 않습니다. 다음 순서로 확장하면 됩니다.

## 1. 샘플 Android 프로젝트 템플릿화

- `AndroidManifest.xml`의 package/application label을 토큰화
- `res/values/colors.xml`을 generator 출력으로 교체
- drawable 리소스 슬롯을 theme.json asset map과 연결

## 2. Docker Gradle worker

```text
POST /api/export/android-apk
  ↓
build_jobs row 생성
  ↓
worker container
  ↓
템플릿 프로젝트 복사
  ↓
리소스 생성
  ↓
./gradlew assembleRelease
  ↓
APK 서명
  ↓
다운로드 URL 저장
```

## 3. 보안 체크리스트

- 사용자 업로드 파일 확장자와 magic bytes 검증
- 파일 크기 제한
- build 작업별 임시 디렉터리 격리
- 컨테이너 network off 또는 allowlist
- 작업 후 임시 파일 삭제
- Gradle dependency cache는 읽기 전용에 가깝게 운용

## 4. 9-patch/말풍선

Android 말풍선은 `.9.png` 관리가 핵심입니다. 웹 편집기에서 stretch/content 영역을 한 번 지정하고 다음 두 출력을 동시에 만들면 됩니다.

- iOS: CSS edge insets + PNG
- Android: `.9.png` + drawable selector
