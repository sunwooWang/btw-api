import time
import os
import jwt
import requests
from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

# 환경변수 또는 기본값 (실서버에서는 .env에 설정)
CLIENT_ID = os.environ.get("NAVERWORKS_CLIENT_ID", "B87SQRQilTrHjOYtoPrp")
CLIENT_SECRET = os.environ.get("NAVERWORKS_CLIENT_SECRET", "HDnmuOZDsC")
SERVICE_ACCOUNT = os.environ.get("NAVERWORKS_SERVICE_ACCOUNT", "ni9fl.serviceaccount@viewtongworld.com")
PRIVATE_KEY = os.environ.get("NAVERWORKS_PRIVATE_KEY", """-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCZjyE1j93eBBmN
1kiZ/UezQd+gxrW8Avz5iGyh1BVeLD+PlJd9AgjHSePJGXupW9sJZdR5EUBBABa4
lqeVy7o8CzyvC/qa+v0Tmw2u1SHpqDbY/9g43Y/j1eIfJJFBRlctY+xJNYnTtrgy
0nGKhSWphY2NXht2NvXTit/aakZfmFYbbhSPZZ5pw8bVg9lialUxVNkLlDUUt+m2
z6Gam22MUWnuc0T61sfEbZiGd865yQiG5o3x7L6lulfBtAdtn2S4MgBk2uA8DqBN
cqa9i8GM/+NwYRkKyodpN+seDOPpSX7pstF/okYkWaz8ooEuEYT/3YtH1foBB9iy
WMngLPB5AgMBAAECggEALDockvwuJyEgKQlUHMHlsjvhSEGjGxTzPn1r6EoYo2h0
IArofLEmzRs7d3KW+sbBddn10a7FxlLbuGtvtgWYzG1iG3qEQbnTRR/N15J8M3tm
3KYHZQ1vQWwbNeQGz/mN5z1V0xoP6cHBGKYi3IYPvF0CUXqOx0P6FmTzp0kfnq1j
XmGOAAj910YZuHD3mJP3eQgevzdO+8beR1jeSq8xGQDDVki4KOsRAWzBgCnH7slW
feMGfGd5JwwPCFHXnxs2ipCwTrPCpDcuHavBdSFhlWpSC5T4mpCAKj6gmKr5dQvC
8mylIHsAg8ddmMdZZSDfeDp8eKJlbebx1ZQoHc+RdwKBgQC25uKe7EAW8bB7xdI2
+0Zn7zKM2Y28MhZq6ns0bOi/Minl75CA1MqK2hGmASA/Ap+fjCsfv8YqcLyxvbyI
d6ubTok95YjzBr8rIxz8LSGAsmzE6ND4FX4KakAro1rLn+FLYplqDC+Z7miFLbB+
29Rug7wKOUkXwlNwcqFMMNoOTwKBgQDW7h2OlZrAhC5E6roCPfhpIAsRZ2nc2NBF
lOQPD3la5+l9S4whHjnWF1DEGqe4uI/S7VNJCtAk3WvbUyPP+Hhrdg1hz7YN5PKo
frBNlmst8Y7Hnzx47mTe4WCIz7fnnEcu7y1R7O0N8gkyYp18IHlWkQuAwb9ULg7y
l+oHd6BqtwKBgQCQQ1SEXXu/nSrCtam1TESgPf71MbOluSwNcJ11IGIETKDXiDnG
JBENrCs3cLPqfztAMOLiy/SWDQ4Ic8t9KEbm3O9LLvzyE2Q9thhqn35JcHJybeBF
jU45EM1EnjhDW/vr5f1zs+Dn3S/7u6n2pZXNBYMP3VdVsiT2ELRA0Fdt6QKBgQCB
JB3aWIXdew6aFjehtT6XW8uKr4pqSlQKGwZVDkUqnAItaMFP/Otfei7rReDVGwBA
Cp1qW/boz6pI5FG2WmNwnkQ4KygGfTRYjZa9Z84KkwPpagJZ31P4n47zZWvo3Hvg
9ZFTknp1UKK6BYr+1DxUCV7SBJhDqlEM7r6NshFPTQKBgHAtxZfj8+f7RLPnV62K
yqhOB1D7VCkWtSmV7o136sf929iTmDTNXxWKSptT04cJGEnJ2Jb2q2cAYwU9gtK1
oIMkpeCDOeK9Siv21JuZpQsu0eB+GreyeITeBzBnLlwJeO8YUcq+5eenLQAANKwZ
iWOzFx0p16zZJfHRLYSr8Rqi
-----END PRIVATE KEY-----""")


class BoardPostRequest(BaseModel):
    board_id: str
    title: str
    content: str


def _get_access_token() -> Optional[str]:
    current_time = int(time.time())
    payload = {
        "iss": CLIENT_ID,
        "sub": SERVICE_ACCOUNT,
        "iat": current_time,
        "exp": current_time + 3600,
    }
    assertion = jwt.encode(payload, PRIVATE_KEY, algorithm="RS256", headers={"alg": "RS256", "typ": "JWT"})

    print("[주석처리] 네이버웍스 토큰 발급 요청 생략")
    return "MOCK_TOKEN"

    # --- 실서버 사용 시 위 2줄 삭제 ---
    # response = requests.post(
    #     "https://auth.worksmobile.com/oauth2/v2.0/token",
    #     headers={"Content-Type": "application/x-www-form-urlencoded"},
    #     data={
    #         "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
    #         "assertion": assertion,
    #         "client_id": CLIENT_ID,
    #         "client_secret": CLIENT_SECRET,
    #         "scope": "board",
    #     },
    # )
    # if response.status_code == 200:
    #     return response.json().get("access_token")
    # return None


@router.post("/board/post")
def board_post(req: BoardPostRequest):
    """네이버웍스 게시판에 글을 작성한다."""
    token = _get_access_token()
    if not token:
        return {"status": "error", "message": "토큰 발급 실패"}

    print(f"[주석처리] 네이버웍스 게시판 업로드. board_id={req.board_id}, title={req.title}")
    return {"status": "ok", "message": "MOCK - 실제 전송 안 됨", "board_id": req.board_id, "title": req.title}

    # --- 실서버 사용 시 위 2줄 삭제 ---
    # url = f"https://www.worksapis.com/v1.0/boards/{req.board_id}/posts"
    # response = requests.post(
    #     url,
    #     headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    #     json={"title": req.title, "body": req.content},
    # )
    # if response.status_code == 201:
    #     return {"status": "ok", "post_id": response.json().get("postId")}
    # return {"status": "error", "message": response.text}
