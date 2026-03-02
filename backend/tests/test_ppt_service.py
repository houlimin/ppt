import pytest
from app.services.ppt_service import PPTGenerator, ThemeConfig, THEMES


class TestPPTGenerator:
    def test_create_title_slide(self):
        generator = PPTGenerator()
        slide = generator.create_title_slide("Test Title", "Test Subtitle")
        
        assert slide is not None
        assert len(generator.prs.slides) == 1
    
    def test_create_content_slide(self):
        generator = PPTGenerator()
        slide = generator.create_content_slide(
            "Test Content",
            ["Point 1", "Point 2", "Point 3"],
            "single_column"
        )
        
        assert slide is not None
        assert len(generator.prs.slides) == 1
    
    def test_create_section_slide(self):
        generator = PPTGenerator()
        slide = generator.create_section_slide("Section 1", 1)
        
        assert slide is not None
        assert len(generator.prs.slides) == 1
    
    def test_create_ending_slide(self):
        generator = PPTGenerator()
        slide = generator.create_ending_slide("Thank You", "contact@example.com")
        
        assert slide is not None
        assert len(generator.prs.slides) == 1
    
    def test_generate_from_json(self):
        generator = PPTGenerator()
        content = {
            "title": "Test Presentation",
            "pages": [
                {
                    "page_index": 1,
                    "title": "Introduction",
                    "content": ["Point 1", "Point 2"],
                    "layout_type": "single_column"
                },
                {
                    "page_index": 2,
                    "title": "Content",
                    "content": ["Point A", "Point B", "Point C"],
                    "layout_type": "two_column"
                }
            ]
        }
        
        prs = generator.generate_from_json(content)
        
        assert prs is not None
        assert len(generator.prs.slides) == 4  # title + 2 content + ending
    
    def test_save_to_bytes(self):
        generator = PPTGenerator()
        generator.create_title_slide("Test")
        
        ppt_bytes = generator.save_to_bytes()
        
        assert ppt_bytes is not None
        assert len(ppt_bytes) > 0
        assert ppt_bytes[:4] == b'PK\x03\x04'  # ZIP file signature (PPTX is a ZIP)
    
    def test_different_themes(self):
        generator = PPTGenerator("business_blue")
        generator.create_title_slide("Blue Theme")
        
        generator2 = PPTGenerator("creative_orange")
        generator2.create_title_slide("Orange Theme")
        
        assert generator.theme != generator2.theme
    
    def test_custom_theme(self):
        custom_theme = ThemeConfig(
            primary_color=(255, 0, 0),
            secondary_color=(0, 255, 0),
            accent_color=(0, 0, 255)
        )
        
        generator = PPTGenerator()
        generator.set_theme(custom_theme)
        
        assert generator.theme.primary_color.rgb == (255, 0, 0)
    
    def test_two_column_layout(self):
        generator = PPTGenerator()
        slide = generator.create_content_slide(
            "Two Column",
            ["A", "B", "C", "D"],
            "two_column"
        )
        
        assert slide is not None
    
    def test_three_column_layout(self):
        generator = PPTGenerator()
        slide = generator.create_content_slide(
            "Three Column",
            ["A", "B", "C", "D", "E", "F"],
            "three_column"
        )
        
        assert slide is not None


class TestThemeConfig:
    def test_default_theme(self):
        theme = ThemeConfig()
        
        assert theme.primary_color.rgb == (0, 112, 192)
        assert theme.title_font == "微软雅黑"
    
    def test_custom_theme(self):
        theme = ThemeConfig(
            primary_color=(255, 0, 0),
            title_font="Arial"
        )
        
        assert theme.primary_color.rgb == (255, 0, 0)
        assert theme.title_font == "Arial"


class TestThemes:
    def test_themes_exist(self):
        assert "business_blue" in THEMES
        assert "education_green" in THEMES
        assert "creative_orange" in THEMES
    
    def test_all_themes_are_theme_config(self):
        for name, theme in THEMES.items():
            assert isinstance(theme, ThemeConfig)
