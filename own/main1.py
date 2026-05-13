import re,requests
from bs4 import BeautifulSoup

class get_text_from_xml():
    def __init__(self):
        self.url_list = [
            'article/how-to-build-a-low-stress-morning-routine.html',
            'article/the-difference-between-tired-and-burning-outand-why-it-matters.html',
            'article/the-sunday-reset-routine-that-eases-your-monday-anxiety.html',
            'article/quiet-hobbies-that-heal-a-burnt-out-brain.html',
            'article/from-sofa-to-sunrise-hike-choose-your-ideal-weekend-reset.html',
            'article/why-mindful-meetings-fewer-meetings-and-better-ones.html',
            'article/reclaiming-the-first-30-minutes-of-your-workday.html',
            'article/how-to-talk-to-your-boss-about-burnout-without-looking-weak.html',
            'article/how-to-recognize-stress-before-it-wrecks-your-week.html',
            'article/breathing-techniques-that-actually-help-during-a-work-crisis.html',
            'article/the-office-stress-triggers-you-didnt-realize-were-draining-you.html',
            'article/6-micro-habits-that-stop-burnout-before-it-starts.html',
            'article/the-difference-between-tired-and-burning-outand-why-it-matters.html',
            'article/work-hard-rest-smart-how-high-performers-avoid-collapse.html',
            'article/5-minute-mindfulness-routines-for-your-overloaded-brain.html',
            'article/how-to-work-slowerand-get-more-done.html',
            'article/the-email-mindfulness-hack-that-changes-your-whole-day.html',
            'article/7-weekend-rituals-that-actually-recharge-your-energy.html',
            'article/why-doing-nothing-on-saturday-might-be-your-power-move.html',
            'article/digital-detox-weekends-how-to-start-without-fomo.html',
        ]
        self.url_list1 = [
            'content/3-1.html',
            'content/3-2.html',
            'content/3-3.html',
            'content/3-4.html',
            'content/3-5.html',
            'content/3-6.html'
        ]
    def extract_text_from_html(self,html_content):
        soup = BeautifulSoup(html_content, 'html.parser')

        # 移除脚本和样式标签
        for script in soup(["script", "style"]):
            script.decompose()

        # 提取所有文本内容
        text = soup.get_text()

        # 清理文本：移除多余的空格和换行
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)

        return text
    def get_xml_text(self):
        headers = {
            'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',

        }
        for url in self.url_list1:
            res = requests.get(url=f'https://chromatic.designcarlossimao.com/{url}',headers=headers)
            text = self.extract_text_from_html(html_content=res.text)
            # with open(f'./file/{url.replace(r"article/","").replace(".html",".txt")}','w',encoding='utf-8') as fp:
            #     fp.write(text)
            #     fp.close()
            with open(f'./file/{url.replace(r"content/", "").replace(".html", ".txt")}', 'w', encoding='utf-8') as fp:
                fp.write(text)
                fp.close()


if __name__ == "__main__":
    gtfx = get_text_from_xml()
    gtfx.get_xml_text()
    # all_text = gtfx.extract_text_from_html()
    #
    # # 打印提取的文本
    # print("提取的完整文本内容：")
    # print("=" * 80)
    # print(all_text)