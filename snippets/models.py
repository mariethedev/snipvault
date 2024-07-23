from django.db import models
from pygments.lexers import get_all_lexers
from pygments.styles import get_all_styles
from pygments.lexers import get_lexer_by_name
from pygments.formatters.html import HtmlFormatter
from pygments import highlight

LEXERS = [item for item in get_all_lexers() if item[1]]
LANGUAGE_CHOICES = sorted([(item[1][0], item[0]) for item in LEXERS])
STYLE_CHOICES = sorted([(item,item) for item in get_all_styles()])

class Snippet(models.Model):
    created = models.DateTimeField(auto_now_add= True)
    title = models.CharField(max_length=100, blank = True, default= '')
    code = models.TextField()
    linenos = models.BooleanField(default=True)
    language = models.CharField(choices = LANGUAGE_CHOICES, default= 'python', max_length= 100)
    style = models.CharField(choices = STYLE_CHOICES, default='friendly', max_length=100)
    owner = models.ForeignKey('authentication.User', related_name='snippets', on_delete=models.CASCADE, default='')
    highlighted = models.TextField(default= '', blank= True)
    description = models.TextField(blank = True, default='')
    tags = models.CharField(max_length=200, blank = True, default = '')
    
    class Meta:
        ordering = ['created']
        
    def save(self, *args, **kwargs):
        
        lexer = get_lexer_by_name(self.language)
        linenos = 'table' if self.linenos else False
        options = {'title': self.title} if self.title else {}
        formatter = HtmlFormatter(style = self.style, linenos = linenos, full = True, **options)
        self.highlighted = highlight(self.code, lexer, formatter)
        
        super().save(*args, **kwargs)
        
    
    def __str__(self):
        return self.title
        

class SharedSnippet(models.Model):
    snippet = models.ForeignKey(Snippet, on_delete=models.CASCADE)
    shared_with = models.ForeignKey('authentication.User', on_delete=models.CASCADE)
    can_edit = models.BooleanField(default='False')
    
    class Meta:
        unique_together = ('snippet', 'shared_with',)
        
    def __str__(self):
        return f"{self.snippet.title} shared with {self.shared_with.email}"