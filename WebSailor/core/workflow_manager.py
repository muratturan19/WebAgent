from tool_search import Search as ToolSearch


class WorkflowManager:
    def __init__(self, page=None):
        self.page = page

    def parse_real_estate_query(self, query):
        return {
            "category_path": [],
            "keywords": query.split() if isinstance(query, str) else query,
        }

    async def process_search_request(self, query):
        try:
            parsed = self.parse_real_estate_query(query)

            search_tool = ToolSearch()
            nav_success, nav_msg = await search_tool.navigate_to_category(
                self.page, parsed["category_path"]
            )

            if not nav_success:
                return {"error": nav_msg}

            results = await search_tool.search_with_filters(self.page, parsed)
            return results

        except Exception as e:
            return {"error": f"Workflow failed: {e}"}

    async def handle_login_redirect(self, page):
        """Handle redirect from Bana Özel back to main page"""
        current_url = page.url
        if "banaozel" in current_url:
            await page.click('a[href="https://www.sahibinden.com"] img, .logo')
            await page.wait_for_load_state('networkidle')

