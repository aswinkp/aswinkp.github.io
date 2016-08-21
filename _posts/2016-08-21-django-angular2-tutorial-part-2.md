---
layout:     post
title:      Django with Angular2 Tutorial -part 2
date:       2016-08-21 10:30:29
summary:    Rendering template with Django and Angular2.
categories: django, angular2, tutorial
---

## Django with Angular2 Tutorial - Rendering templates

This tutorial is the sequel of [Django with Angular2 Tutorial - Getting Started](https://4sw.in/blog/2016/django-angular2-tutorial/). You would get a better understanding by reading the above if you are starting to integrate Angular2 with Django.

Part 2 focuses on rendering django context variables and angular2 string interpolation in same html file. 

As far as my experience jinja2 stands as a best templating engine for django. Some benchmarks even say that Jinja2's performance is 20 times of that of django. Although django templating engine is good, I prefer Jinja2 for its performance and features.

Both Angular2 and jinja2 has `{% raw %}{{ }}{% endraw %}`</pre> syntax in their templates. Luckily jinja2 offers to change those syntax. Not sure that Django would provide this.

### Into Action

Continuing from the first part of this tutorial series. [https://4sw.in/blog/2016/django-angular2-tutorial/](https://4sw.in/blog/2016/django-angular2-tutorial/) .

> Download the source code [HERE](https://github.com/aswinkp/django-ng2-starter).

First install Jinja2 in  the virtualenv

```bash
pip install jinja2
```

In `settings.py` file add jinja2 in template backend.  

```python
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.jinja2.Jinja2',
        'DIRS': ['jinja2'],
        'APP_DIRS': True,
        'OPTIONS': {
            'variable_start_string': '[{',
            'variable_end_string': '}]',
        },
    },
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        .
        .
        .
    },
]
```

Note the `OPTIONS` in the Jinja2 backend. We are changing the default jinja2 delimiter from `{% raw %}{{ }}{% endraw %}` to `[{ }]`. This is to ensure that there is no conflict between the default jinja2 delimiter and angular2 interpolation.

```typescript
import {Component} from "@angular/core";
@Component({
  templateUrl: '/sample/ng/'
})
export class DjangoComponent{

}

```
In `app.routes.ts`

`import {DjangoComponent} from "./django.component";`

and create a route

`{ path: 'djcomponent', component: DjangoComponent },`

Also add the below line inside `nav` tag `app.component.ts` 

`<a routerLink="/djcomponent" routerLinkActive="active">Django Component</a>`


In `views.py` add the following class.
 
```python
class NgTemplateView(View):
	def get(self, request):
		return render(request, 'template.html', {"django_variable": "This is django context variable"})
```

In `urls.py` add the line under ngurls

`url(r'^ng/$', NgTemplateView.as_view(), name='ngTemplate'),`

Now create a folder inside the app folder named jinja2 create template file `template.html`.

```bash
cd /path/to/app/
mkdir jinja2
cd jinja2
touch templae.html

```

Now in `template.html` paste the following content.

```html
Jinja2 Template with variales from django and angular.
<br>
[{ django_variable }]
<br>
{% raw %}{{ ngVariable }}{% endraw %}
```

Start Django server and npm server.

Visit [http://localhost:8000/djcomponent](http://localhost:8000/djcomponent)


### Happy Coding :)


___



