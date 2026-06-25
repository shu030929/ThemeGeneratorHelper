# MAKETHEME

MAKEETHEME은 CSS/XML을 직접 수정하지 않고 색상과 이미지만 입력해 사용자 테마 파일을 만들 수 있도록 만든 MVP 레포입니다.

이 프로젝트는 **KakaoTalk 사용자 테마 포맷과 호환되는 파일을 생성**하기 위한 비공식 도구입니다. Kakao Corp.와 제휴, 후원, 승인 관계가 없습니다. Kakao, KakaoTalk 및 관련 브랜드는 Kakao Corp.의 상표입니다. 공개 서비스나 배포물에서 공식 제품처럼 보이는 이름, 로고, 캐릭터, 샘플 리소스를 사용하지 마세요.

## 포함 기능

- 웹 UI 기반 색상 편집
- 실시간 채팅 화면 미리보기
- `theme.json` export/import
- iOS `.ktheme` 생성
- Android resource zip 생성
- 브라우저 이미지 업로드 후 data URL 저장
- 순수 Python PNG placeholder 생성
- 외부 샘플 리소스 미포함

## 빠른 실행

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .

python -m makeetheme serve --host 127.0.0.1 --port 8000
```

브라우저에서 열기:

```text
http://127.0.0.1:8000
```

패키지 설치 없이 실행:

```bash
PYTHONPATH=src python3 -m makeetheme serve --host 127.0.0.1 --port 8000
```

## CLI

```bash
PYTHONPATH=src python3 -m makeetheme ios examples/theme.json --out dist/makeetheme-pink.ktheme
PYTHONPATH=src python3 -m makeetheme android-res examples/theme.json --out dist/makeetheme-pink-android-resources.zip
```

패키지 설치 후에는 다음 명령도 사용할 수 있습니다.

```bash
makeetheme ios examples/theme.json --out dist/makeetheme-pink.ktheme
makeetheme android-res examples/theme.json --out dist/makeetheme-pink-android-resources.zip
```

## 웹 API

### `GET /`

웹 에디터를 반환합니다.

### `POST /api/export/ios`

요청 JSON:

```json
{
  "meta": {
    "name": "MAKEETHEME Pink",
    "authorName": "MAKEETHEME",
    "iosThemeId": "com.example.theme.makeethemepink.ios"
  },
  "colors": {
    "mainBackground": "#FFDEDE"
  },
  "assets": {}
}
```

응답: `.ktheme` 파일

### `POST /api/export/android-res`

응답: Android resource zip

## 주의

- 공식 샘플 테마, 캐릭터, 로고, 스크린샷, 가이드 PDF를 레포에 포함하지 마세요.
- 사용자가 업로드한 이미지의 권리는 사용자가 책임져야 합니다.
- Android APK 자동 빌드는 아직 포함하지 않았습니다. 현재는 resource zip까지만 생성합니다.
- 실제 공개 서비스에서는 파일 크기 제한, 확장자 검증, 악성 파일 검사, 빌드 sandbox가 필요합니다.

## 구조

```text
src/makeetheme/
  models.py                # theme.json 검증/merge
  png.py                   # 순수 Python PNG 생성기
  ios/
    css.py                 # iOS 테마 CSS 렌더러
    assets.py              # 기본 PNG asset 생성
    exporter.py            # .ktheme zip 생성
  android/
    resources.py           # colors.xml/resource zip 생성
web/
  index.html
  styles.css
  app.js
```

## 라이선스

MIT
