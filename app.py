import streamlit as st
import pandas as pd
import numpy as np

# 1. st.write 와 st.title 의 기능 
st.write("1. As you can see, it is possible to write text above title.")
st.title("Hello World_Title")
st.write("second line")

# 2. st.write 라는 만능 기능
st.write("2. Here's our first attempt at using data to create a table:")
st.write(
    pd.DataFrame({
        'first col' : [1,2,3,4],
        'second col' : [10, 20, 30, 40]
    }))

# 3. st.dataframe 기능
dataFrame_01 = pd.DataFrame(
    np.random.randn(10, 20),
    columns=('col %d' % i for i in range(20)))
st.write("3. Now lets see the difference between st.dataframe and st.table")
st.dataframe(dataFrame_01.style.highlight_max(color='yellow', axis='index'))
st.table(dataFrame_01)
'''
np.random.randn 과, columns= 인자, 줄 압축? 에 대한 이해 필요\n
https://pandas.pydata.org/docs/reference/api/pandas.io.formats.style.Styler.highlight_max.html
'''

# 4. line chart, map 그리기
st.write('4. Let\'s add line chart and map' )
chart_data = pd.DataFrame(
    np.random.randn(20, 3),
    columns=['a', 'b', 'c']
)
st.line_chart(chart_data)
map_data = pd.DataFrame(
    np.random.randn(100, 2) / [50, 50] + [37.56, 126.97],
    columns=['lat', 'lon']
)
st.map(map_data, size=20, color='#ffff00')
'''
st.map 도대체 어느 부분이 지역을 적용한 거지?\n
단순 np.random.randn 의 범위를 제한한 것 같은데, 이게 어떻게 경도와 위도로 이어지는 거지?\n
https://numpy.org/doc/2.1/reference/random/generated/numpy.random.randn.html \n
https://docs.streamlit.io/develop/api-reference/charts/st.map
'''

#5. 위젯 만들기
st.write('5. We\'ll see some examples of widgets.')
x = st.slider('x')  # 👈 this is a widget
st.write(x, 'squared is', x * x)
'''
1. slide 에 따라 x가 변동되며, 이후 이어지는 문구도 달라진다.\n
2. slide 가 조정될 때마다 난수가 재설정되는 것 같다.
'''

#6. input, output 유형
st.text_input("Your name : ", key='name')
'''
You can access the value at any point with:
'''
st.session_state.name
'''
- 이 부분은 위의 slider 가 조정되어도 유지된다.
- np.random.randn 과는 다름. 
- 세션의 기준이 무엇인가?
- 이 링크에서 구체적으로 나와있는 것 같다.\n
https://docs.streamlit.io/develop/api-reference/caching-and-state/st.session_state
'''

#7. Use checkboxes to show/hide data
'''
- 아래 체크박스에 따라, 가시 여부가 달라진다.
- 주의 : IF 문 안에 대상이 있어야 적용된다.\n
'''
if st.checkbox('Show dataframe'):
    chart_data = pd.DataFrame(
       np.random.randn(20, 3),
       columns=['a', 'b', 'c'])

    chart_data