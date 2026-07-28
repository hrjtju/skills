#!/usr/bin/env python3
"""
IMA Knowledge Base Query Tool — single Python script, no Node.js required.

Usage:
  ima_query.py list-kb                        # List all knowledge bases
  ima_query.py browse <kb_name>               # Browse content of a KB
  ima_query.py search <kb_name> <query>       # Search within a KB
  ima_query.py search-all <query>             # Search across all KBs
  ima_query.py info <media_id>                # Get file info and download URL

Credentials are read from ~/.config/ima/client_id and ~/.config/ima/api_key
"""

import sys
import json
import os
import urllib.request
import urllib.error

BASE_URL = "https://ima.qq.com"
API_BASE = f"{BASE_URL}/openapi/wiki/v1"


def load_credentials():
    cred_dir = os.path.expanduser("~/.config/ima")
    client_id = open(os.path.join(cred_dir, "client_id")).read().strip()
    api_key = open(os.path.join(cred_dir, "api_key")).read().strip()
    return client_id, api_key


def api_call(path, body):
    client_id, api_key = load_credentials()
    url = f"{API_BASE}/{path}"
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "ima-openapi-clientid": client_id,
            "ima-openapi-apikey": api_key,
            "ima-openapi-ctx": "skill_version=1.1.8",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return {"code": -1, "msg": f"HTTP {e.code}: {e.reason}"}
    except Exception as e:
        return {"code": -1, "msg": str(e)}


def list_kb():
    """List all knowledge bases."""
    resp = api_call("search_knowledge_base", {"query": "", "cursor": "", "limit": 20})
    if resp.get("code") != 0:
        return resp
    kbs = resp.get("data", {}).get("info_list", [])
    return [{"id": kb["kb_id"], "name": kb["kb_name"], "count": kb.get("content_count", "?"),
             "description": kb.get("description", ""), "role": kb.get("role_type", "")}
            for kb in kbs]


def find_kb(name_hint):
    """Find a knowledge base by name (fuzzy match)."""
    kbs = list_kb()
    if isinstance(kbs, dict) and kbs.get("code"):
        return kbs
    name_lower = name_hint.lower()
    matches = [kb for kb in kbs if name_lower in kb["name"].lower()]
    if not matches:
        return {"code": -1, "msg": f"No KB matching '{name_hint}'. Available: {[kb['name'] for kb in kbs]}"}
    if len(matches) > 1:
        return {"code": -1, "msg": f"Multiple matches: {[m['name'] for m in matches]}. Please be more specific."}
    return matches[0]


def browse_kb(kb_name, cursor="", limit=50):
    """Browse content of a knowledge base."""
    kb = find_kb(kb_name)
    if isinstance(kb, dict) and kb.get("code"):
        return kb
    resp = api_call("get_knowledge_list",
                    {"knowledge_base_id": kb["id"], "cursor": cursor, "limit": limit})
    if resp.get("code") != 0:
        return resp
    items = resp.get("data", {}).get("knowledge_list", [])
    result = []
    for item in items:
        media_type = item.get("media_type", 0)
        type_str = "📁" if media_type == 999 else "📄"
        result.append({
            "media_id": item.get("media_id", ""),
            "title": item.get("title", ""),
            "type": type_str,
            "media_type": media_type,
            "folder_id": item.get("parent_folder_id", ""),
        })
    return {
        "kb_name": kb["name"],
        "kb_id": kb["id"],
        "items": result,
        "next_cursor": resp.get("data", {}).get("next_cursor", ""),
        "is_end": resp.get("data", {}).get("is_end", True),
    }


def search_kb(kb_name, query, cursor=""):
    """Search within a knowledge base."""
    kb = find_kb(kb_name)
    if isinstance(kb, dict) and kb.get("code"):
        return kb
    resp = api_call("search_knowledge",
                    {"query": query, "knowledge_base_id": kb["id"], "cursor": cursor})
    if resp.get("code") != 0:
        return resp
    items = resp.get("data", {}).get("info_list", [])
    result = []
    for item in items:
        result.append({
            "media_id": item.get("media_id", ""),
            "title": item.get("title", ""),
            "media_type": item.get("media_type", 0),
        })
    return {
        "kb_name": kb["name"],
        "query": query,
        "items": result,
        "total": len(result),
    }


def search_all_kb(query):
    """Search across all knowledge bases."""
    kbs = list_kb()
    if isinstance(kbs, dict) and kbs.get("code"):
        return kbs
    all_results = {}
    for kb in kbs:
        result = search_kb(kb["name"], query)
        if isinstance(result, dict) and result.get("items"):
            all_results[kb["name"]] = result["items"]
    return {"query": query, "results_by_kb": all_results,
            "total_kbs_searched": len(kbs),
            "total_hits": sum(len(v) for v in all_results.values())}


def get_media_info(media_id):
    """Get file info and download URL."""
    resp = api_call("get_media_info", {"media_id": media_id})
    if resp.get("code") != 0:
        return resp
    data = resp.get("data", {})
    info = {
        "media_id": media_id,
        "title": data.get("title", ""),
        "media_type": data.get("media_type", 0),
        "file_size": data.get("file_size", 0),
        "file_ext": data.get("file_ext", ""),
    }
    url_info = data.get("url_info", {})
    if url_info and url_info.get("url"):
        info["download_url"] = url_info["url"]
    notebook = data.get("notebook_ext_info", {})
    if notebook and notebook.get("notebook_id"):
        info["notebook_id"] = notebook["notebook_id"]
    return info


def format_output(data, fmt="json"):
    if fmt == "text":
        if isinstance(data, list):
            for i, kb in enumerate(data):
                print(f"{i+1}. {kb['name']} ({kb['count']} items) [{kb['role']}]")
                if kb.get("description"):
                    print(f"   {kb['description']}")
        elif isinstance(data, dict):
            if "items" in data:
                kb_name = data.get("kb_name", "")
                print(f"📚 {kb_name} ({len(data['items'])} items):")
                for item in data["items"]:
                    print(f"  {item.get('type','')} {item['title']}")
                    print(f"    media_id: {item['media_id']}")
            elif "results_by_kb" in data:
                total = data["total_hits"]
                print(f"🔍 '{data['query']}' → {total} hits across {data['total_kbs_searched']} KBs:")
                for kb_name, items in data["results_by_kb"].items():
                    print(f"\n  📚 {kb_name} ({len(items)} hits):")
                    for item in items[:10]:
                        print(f"    📄 {item['title']}")
                        print(f"       media_id: {item['media_id']}")
                    if len(items) > 10:
                        print(f"    ... and {len(items)-10} more")
            elif "download_url" in data:
                print(f"📄 {data.get('title','')}")
                print(f"   Type: {data.get('media_type')}")
                print(f"   URL: {data.get('download_url','N/A')}")
            else:
                print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(json.dumps(data, indent=2, ensure_ascii=False))


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]

    try:
        if cmd == "list-kb":
            data = list_kb()
        elif cmd == "browse":
            if len(sys.argv) < 3:
                print("Usage: ima_query.py browse <kb_name>")
                sys.exit(1)
            data = browse_kb(sys.argv[2])
        elif cmd == "search":
            if len(sys.argv) < 4:
                print("Usage: ima_query.py search <kb_name> <query>")
                sys.exit(1)
            data = search_kb(sys.argv[2], sys.argv[3])
        elif cmd == "search-all":
            if len(sys.argv) < 3:
                print("Usage: ima_query.py search-all <query>")
                sys.exit(1)
            data = search_all_kb(sys.argv[2])
        elif cmd == "info":
            if len(sys.argv) < 3:
                print("Usage: ima_query.py info <media_id>")
                sys.exit(1)
            data = get_media_info(sys.argv[2])
        else:
            print(f"Unknown command: {cmd}")
            print(__doc__)
            sys.exit(1)

        format_output(data, "text")

    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
