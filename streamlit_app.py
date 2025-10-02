import streamlit as st
from snowflake.snowpark.functions import col


# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")

st.write(
  """Choose the fruits you want in your custom Smoothie!
  """
)

name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

cnz = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
# st.dataframe(data=my_dataframe, use_container_width=True)
# editable_df = st.data_editor(my_dataframe)

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:'
    , my_dataframe
    , max_selections=5
)

orders_df = session.table("smoothies.public.orders").select(
    col("order_uid"),
    col("order_filled"),
    col("name_on_order"),
    col("ingredients")
)

if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        if fruit_chosen == ingredients_list[-1]:
            ingredients_string += fruit_chosen + ' '
        else:
            ingredients_string += fruit_chosen +', '
    
    time_to_insert = st.button('Submit Order')
    # st.write(ingredients_string)

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
        values ('"""+ ingredients_string + """','"""+ name_on_order +"""')"""

    # st.write(my_insert_stmt)
    # st.stop()


    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")
        
        editable_df = st.data_editor(orders_df)
        edited_dataset = session.create_dataframe(editable_df)
        
        og_dataset = session.table("smoothies.public.orders")
        og_dataset.merge(
            edited_dataset,
            (og_dataset['ORDER_UID'] == edited_dataset['ORDER_UID']),
            [when_matched().update({'order_filled': edited_dataset['order_filled']})]
        )

# New section to display smoothiefroot nutrition information
import requests
smoothiefroot_response = requests.get("https://my.smooothiefroot.com/api/fruit/watermelon")
st.text(smoothiefroot_response)
