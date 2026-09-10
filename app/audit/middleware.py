class AuditMiddleware:
    def __init__(self,get_response): self.get_response=get_response
    def __call__(self,request):
        response=self.get_response(request)
        if request.method in {"POST","PUT","PATCH","DELETE"} and getattr(request,"user",None) and request.user.is_authenticated and response.status_code < 400:
            try:
                from .models import AuditEvent
                AuditEvent.objects.create(actor=request.user,action=request.method,object_type="Webaktion",object_repr=request.path[:255],path=request.path[:300])
            except Exception:
                pass
        return response
