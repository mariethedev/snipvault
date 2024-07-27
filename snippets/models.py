from django.db import models
from pygments.lexers import get_all_lexers
from pygments.styles import get_all_styles
from pygments.lexers import get_lexer_by_name
from pygments.formatters.html import HtmlFormatter
from pygments import highlight


class SoftDeleteManager(models.Manager):
    
    #Fetches all items that have not been deleted
    def get_queryset(self):
        return super().get_queryset().filter(deleted = False)
    
    #Fetches all items including that which have been deleted amd that which have not
    def all_with_deleted(self):
        return super().get_queryset()
    
    #Fetches all items which have been deleted
    def deleted(self):
        return super().get_queryset().filter(deleted = True)
    
    def get(self, *args, **kwargs):
        return self.all_with_deleted().get(*args, **kwargs)
    
    def filter(self, *args, **kwargs):
        if 'pk' in kwargs:
            return self.all_with_deleted().get(*args, **kwargs)
        return self.get_queryset().filter(*args, **kwargs)
    
    


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
    deleted = models.BooleanField(default=False)
    
    objects = SoftDeleteManager()
    
    class Meta:
        ordering = ['created']
        
        
    def soft_delete(self):
        self.deleted = True
        self.save()
        
    def restore(self):
        self.deleted = False
        self.save()
        
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
    snippet = models.ForeignKey(Snippet, on_delete=models.CASCADE, related_name='shared_snippet')
    shared_with = models.ForeignKey('authentication.User', on_delete=models.CASCADE)
    can_edit = models.BooleanField(default='False')
    shared_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('snippet', 'shared_with',)
        
        
    def __str__(self):
        return f"{self.snippet.title} shared with {self.shared_with.email}"
    
    
class Note(models.Model):
    snippet = models.OneToOneField(Snippet, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
    def __str__(self):
        return f"Note for snippet {self.snippet.id}"