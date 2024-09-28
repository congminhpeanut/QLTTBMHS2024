from django.shortcuts import render

# Create your views here.
# score_app/views.py
from django.shortcuts import render, redirect
from django.http import HttpResponse
import pandas as pd

import os
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render

# Global variable to store the DataFrame
df = pd.DataFrame()
locdf = df.copy()
lochoten,locto,locnhom,locghichu = '','','',''
openfilename = ''

def index(request):
    if request.method == 'POST':
        file = request.FILES['file']
        header_row = int(request.POST.get('header_row', 1))  # Default to the first row

        # Read the uploaded Excel file
        global df
        global locdf
        global openfilename

        openfilename = file.name
        df = pd.read_excel(file, header=header_row-1)

        # Filter required columns and rename them for consistency

        if len(df.columns) == 6:
            df.columns = ['STT', 'MSSV', 'Họ tên',
                      'Tổ',  # Apply custom class for column width
                      'Nhóm',  # Apply custom class for column width
                      'Ghi chú']  # Rename columns

        # Add new columns with default values
        new_columns = ['Điểm CC Bài 1', 'Điểm TT Bài 1', 'Điểm CC Bài 2', 'Điểm TT Bài 2',
                       'Điểm CC Bài 3', 'Điểm TT Bài 3', 'Điểm LT thi', 'Điểm TT thi', 'Điểm TK']
        for col in new_columns:
            if col not in df.columns:
                if 'CC' in col:
                    df[col] = 0.5  # Default float values
                else:
                    df[col] = 0.0

        df.fillna(value='', inplace=True)  # Fill NaN values with an empty string

        if 'STT' in df.columns:
            df.drop('STT', axis=1, inplace=True)

        df['Điểm TK'] = df['Điểm CC Bài 1'] + df['Điểm CC Bài 2'] + df['Điểm CC Bài 3'] + \
                        df['Điểm TT Bài 1'] + df['Điểm TT Bài 2'] + df['Điểm TT Bài 3'] + \
                        df['Điểm LT thi'] + df['Điểm TT thi']
        df['MSSV'] = df['MSSV'].astype(str)
        df['Họ tên'] = df['Họ tên'].astype(str)
        df['Tổ'] = df['Tổ'].astype(str)
        df['Nhóm'] = df['Nhóm'].astype(str)
        df['Ghi chú'] = df['Ghi chú'].astype(str)

        locdf = df.copy()

        #df.set_index(df.columns[0], drop=True, inplace=True)
        #df.index.name=''

        return redirect('display_excel')  # Redirect to display view after processing

    return render(request, 'index.html')  # Render the file upload form

def display(request):
    if request.method == 'POST':
        #file = request.FILES['file']
        #header_row = int(request.POST.get('header_row', 1))  # Default to the first row

        global df
        global locdf, lochoten, locto, locnhom, locghichu

        lochoten = str(request.POST.get('filter-name',''))
        locto = str(request.POST.get('filter-to', ''))
        locnhom = str(request.POST.get('filter-nhom', ''))
        locghichu = str(request.POST.get('filter-ghichu', ''))

        locdf = df.copy()

        loctolastring = 0
        if lochoten.strip() != '':
            locdf = locdf[locdf['Họ tên'].str.contains(lochoten.strip(), case=False)]
        if locto.strip() != '':
            for alpha in locto:
                if alpha.lower() in 'abcdefghijklmnopqrstuvwxyz':
                    loctolastring = 1
                    locdf = locdf[locdf['Tổ'].str.contains(locto.strip(), case=False)]
                    break
            if loctolastring == 0:
                locdf = locdf[locdf['Tổ'] == locto.strip()]
        if locnhom.strip() != '':
            locdf = locdf[locdf['Nhóm'] == locnhom.strip()]
        if locghichu.strip() != '':
            locdf = locdf[locdf['Ghi chú'].str.contains(locghichu.strip(), case=False)]

        if locdf.empty:
            return HttpResponse("Không tìm thấy dữ liệu.")

        return redirect('display_excel')  # Redirect to display view after processing

    return render(request, 'display.html')  # Render the file upload form

def display_excel(request):
    global df
    global locdf, lochoten, locto, locnhom, locghichu

    if df.empty:
        return HttpResponse("Không thấy dữ liệu.")

    df['Điểm TK']= df['Điểm CC Bài 1'] + df['Điểm CC Bài 2'] + df['Điểm CC Bài 3'] +\
                   df['Điểm TT Bài 1'] + df['Điểm TT Bài 2'] + df['Điểm TT Bài 3'] +\
                   df['Điểm LT thi'] + df['Điểm TT thi']
    # Convert DataFrame to HTML
    html_table = df.to_html(classes='table table-striped', index=False)

    # Replace column headers with custom classes
    html_table = html_table.replace(
    '<th>MSSV</th>', '<th>MSSV</th>'
    ).replace(
    '<th>Tổ</th>', '<th class="column-to">Tổ</th>'
    ).replace(
    '<th>Nhóm</th>', '<th class="column-nhom">Nhóm</th>'
    )

    # Convert DataFrame (LOC) to HTML
    if ~locdf.empty:
       html_tableloc = locdf.to_html(classes='table table-striped', index=False)
       html_tableloc = html_tableloc.replace(
           '<th>MSSV</th>', '<th>MSSV</th>'
       ).replace(
           '<th>Tổ</th>', '<th class="column-to">Tổ</th>'
       ).replace(
           '<th>Nhóm</th>', '<th class="column-nhom">Nhóm</th>'
       )

    # Render the DataFrame as an HTML table
    if locdf.empty:
        return render(request, 'display.html', {'df': html_table})
    else:
        lochoten,locto,locnhom,locghichu = '','','',''
        return render(request, 'display.html', {'df': html_tableloc})

def update_row(request):
    global df
    if request.method == 'POST':
        row_index = str(request.POST.get('mssv_index'))

        # Update the DataFrame with new values
        df.loc[df['MSSV'] == row_index, 'Điểm CC Bài 1'] = float(request.POST.get('diem_b1_cc'))
        df.loc[df['MSSV'] == row_index, 'Điểm TT Bài 1'] = float(request.POST.get('diem_b1_tt'))
        df.loc[df['MSSV'] == row_index, 'Điểm CC Bài 2'] = float(request.POST.get('diem_b2_cc'))
        df.loc[df['MSSV'] == row_index, 'Điểm TT Bài 2'] = float(request.POST.get('diem_b2_tt'))
        df.loc[df['MSSV'] == row_index, 'Điểm CC Bài 3'] = float(request.POST.get('diem_b3_cc'))
        df.loc[df['MSSV'] == row_index, 'Điểm TT Bài 3'] = float(request.POST.get('diem_b3_tt'))
        df.loc[df['MSSV'] == row_index, 'Điểm LT thi'] = float(request.POST.get('diemthi_lt'))
        df.loc[df['MSSV'] == row_index, 'Điểm TT thi'] = float(request.POST.get('diemthi_tt'))
        df.loc[df['MSSV'] == row_index, 'Ghi chú'] = request.POST.get('ghi_chu')

        if ~locdf.empty:
            locdf.loc[locdf['MSSV'] == row_index, 'Điểm CC Bài 1'] = float(request.POST.get('diem_b1_cc'))
            locdf.loc[locdf['MSSV'] == row_index, 'Điểm TT Bài 1'] = float(request.POST.get('diem_b1_tt'))
            locdf.loc[locdf['MSSV'] == row_index, 'Điểm CC Bài 2'] = float(request.POST.get('diem_b2_cc'))
            locdf.loc[locdf['MSSV'] == row_index, 'Điểm TT Bài 2'] = float(request.POST.get('diem_b2_tt'))
            locdf.loc[locdf['MSSV'] == row_index, 'Điểm CC Bài 3'] = float(request.POST.get('diem_b3_cc'))
            locdf.loc[locdf['MSSV'] == row_index, 'Điểm TT Bài 3'] = float(request.POST.get('diem_b3_tt'))
            locdf.loc[locdf['MSSV'] == row_index, 'Điểm LT thi'] = float(request.POST.get('diemthi_lt'))
            locdf.loc[locdf['MSSV'] == row_index, 'Điểm TT thi'] = float(request.POST.get('diemthi_tt'))
            locdf.loc[locdf['MSSV'] == row_index, 'Ghi chú'] = request.POST.get('ghi_chu')
            locdf['Điểm TK'] = locdf['Điểm CC Bài 1'] + locdf['Điểm CC Bài 2'] + locdf['Điểm CC Bài 3'] + \
                        locdf['Điểm TT Bài 1'] + locdf['Điểm TT Bài 2'] + locdf['Điểm TT Bài 3'] + \
                        locdf['Điểm LT thi'] + locdf['Điểm TT thi']
        # Handle other "Điểm" columns similarly...

    return redirect('display_excel')

def save(request):
    if request.method == 'POST':
        global df
        global openfilename

        # Define the file name and file path where the Excel file will be saved
        file_name = openfilename
        file_path = os.path.join(settings.MEDIA_ROOT, file_name)

        # Save the DataFrame to the Excel file
        df.to_excel(file_path, index=False)

        # Optionally, return a response or redirect
        return HttpResponse(f"Lưu file thành công: {file_path}")

    return render(request, 'display.html')  # Render the file upload form