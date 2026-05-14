from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from collections import defaultdict
from .models import TaxReturn, RETURN_TYPE_CHOICES
from .forms import TaxReturnForm
from core.tenancy import company_required, get_company


@company_required
def returns_list(request):
    company = get_company(request.user)
    filter_type = request.GET.get('type', '')
    filter_year = request.GET.get('year', '')

    qs = TaxReturn.objects.filter(company=company)
    if filter_type:
        qs = qs.filter(return_type=filter_type)
    if filter_year:
        qs = qs.filter(year=filter_year)

    # Build grouped structure: {return_type_label: {year: [entries]}}
    type_label_map = dict(RETURN_TYPE_CHOICES)
    grouped = defaultdict(lambda: defaultdict(list))
    all_years = set()

    for entry in qs.order_by('return_type', '-year', '-month'):
        grouped[entry.return_type][entry.year].append(entry)
        all_years.add(entry.year)

    grouped_data = []
    for rtype, years_dict in sorted(grouped.items()):
        years = [
            {'year': yr, 'entries': entries}
            for yr, entries in sorted(years_dict.items(), reverse=True)
        ]
        total = sum(len(y['entries']) for y in years)
        filed = sum(
            1 for y in years for e in y['entries'] if e.status == 'Filed'
        )
        grouped_data.append({
            'return_type': rtype,
            'label': type_label_map.get(rtype, rtype),
            'years': years,
            'total': total,
            'filed': filed,
        })

    return render(request, 'returns/list.html', {
        'grouped_data': grouped_data,
        'return_type_choices': RETURN_TYPE_CHOICES,
        'all_years': sorted(all_years, reverse=True),
        'filter_type': filter_type,
        'filter_year': filter_year,
    })


@company_required
def return_create(request):
    company = get_company(request.user)
    if request.method == 'POST':
        form = TaxReturnForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.company = company
            obj.save()
            messages.success(request, f'{obj.return_type} return saved.')
            return redirect('returns:list')
    else:
        form = TaxReturnForm()
    return render(request, 'returns/form.html', {'form': form, 'title': 'Add Return'})


@company_required
def return_edit(request, pk):
    company = get_company(request.user)
    obj = get_object_or_404(TaxReturn, pk=pk, company=company)
    if request.method == 'POST':
        form = TaxReturnForm(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Return updated.')
            return redirect('returns:list')
    else:
        form = TaxReturnForm(instance=obj)
    return render(request, 'returns/form.html', {'form': form, 'title': f'Edit {obj.return_type}', 'obj': obj})


@company_required
def return_delete(request, pk):
    company = get_company(request.user)
    obj = get_object_or_404(TaxReturn, pk=pk, company=company)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Return deleted.')
        return redirect('returns:list')
    return render(request, 'returns/confirm_delete.html', {'obj': obj})
