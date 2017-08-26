import pandas as pd


class ABC_Analysis():

    def __init__(self, filepath):
        self.file = filepath
        try:
            self.df = pd.read_csv(self.file, encoding='utf-8')
        except UnicodeDecodeError as e:
            print('Incorrect encoding. Ecoding must be utf-8')
        except FileNotFoundError as e:
            print('File does not exist at the specified location')
        except AttributeError as e:
            print('File is not formated in the desired way. There'
                  'must be atleast 3 columns. Order IDs column should be name "orderID"'
                  'Quantity column should be named "Quantity" AND '
                  'Value of the product should be named "Value"')

    def Top80Percent(self):
        top80 = []
        for i in range (0, len(Cumm_percent)):
            if (Cumm_percent[i]<= 80.0): top80.append('1')
            else: top80.append('0')
        return top80


    def Top80Percent_Qty(self):
        top80 = []
        for i in range (0, len(Cumm_percent_Qty)):
            if (Cumm_percent_Qty[i]<= 80.0): top80.append('1')
            else: top80.append('0')
        return top80

    def Top80Percent_Value(self):
        top80 = []
        for i in range (0, len(Cumm_percent_Value)):
            if (Cumm_percent_Value[i]<= 80.0): top80.append('1')
            else: top80.append('0')
        return top80

    def calc_abc_orders(self):

        orderID = self.df['OrderID']
        Quantity = self.df['Quantity']
        Value = self.df['Value']

        FrequencySeries = pd.Series(orderID)  # Get all orderID or items in a dataframe

        # Handling Frequency Sheet
        Frequency = FrequencySeries.value_counts()
        freqSum = sum(Frequency)

        CummSum = Frequency.cumsum()
        Cumm_percent = 100 * CummSum / sum(Frequency)

        Freq_DataFrame = pd.Series.to_frame(Cumm_percent)
        Freq_DataFrame.index.name = 'OrderID'
        Freq_DataFrame['Top_80_Freq'] = Top80Percent()  # Return cummulative percentage dataframe for frequency
        Freq_DataFrame.columns = ['Frequency', 'Top_80_Freq']

        # Handling Quantity
        Groupby_qty = Quantity.groupby(orderID, sort=True).sum()
        Quantity_Series = Groupby_qty.sort_values(ascending=False)

        QtySum = sum(Groupby_qty)

        CummSum_Qty = Quantity_Series.cumsum()
        Cumm_percent_Qty = 100 * CummSum_Qty / QtySum

        Qty_DataFrame = pd.Series.to_frame(Cumm_percent_Qty)
        # Qty_DataFrame.set_index('OrderID', inplace=True)
        Qty_DataFrame.index.name = 'OrderID'
        Qty_DataFrame['Top_80_Qty'] = Top80Percent_Qty()  # Return cummulative percentage dataframe for Quantity

        # Handling Value
        Groupby_Value = Value.groupby(orderID, sort=True).sum()
        Value_Series = Groupby_Value.sort_values(ascending=False)

        ValueSum = sum(Groupby_Value)

        CummSum_Value = Value_Series.cumsum()
        Cumm_percent_Value = 100 * CummSum_Value / ValueSum

        Value_DataFrame = pd.Series.to_frame(Cumm_percent_Value)
        # Value_DataFrame.set_index('OrderID', inplace=True)
        Value_DataFrame.index.name = 'OrderID'
        Value_DataFrame['Top_80_Value'] = Top80Percent_Value()  # Return cummulative percentage dataframe for Quantity

        # Merging DataFrames
        merge_Two_DataFrames = pd.merge(Value_DataFrame, Qty_DataFrame, left_index=True, right_index=True)
        Main_DataFrame = pd.merge(merge_Two_DataFrames, Freq_DataFrame, left_index=True, right_index=True)
        Main_DataFrame.reset_index(level=0, inplace=True)  # Converting Index to Column

        SKUs = Main_DataFrame['OrderID']
        value_cal = Main_DataFrame['Top_80_Value']
        Qty_cal = Main_DataFrame['Top_80_Qty']
        Freq_cal = Main_DataFrame['Top_80_Freq']

        Req_List = {}
        for i in range(len(SKUs)):
            if (int(value_cal[i]) + int(Qty_cal[i]) + int(Freq_cal[i]) == 3):
                Req_List.update({SKUs[i]: 'A'})
            elif (int(value_cal[i]) + int(Qty_cal[i]) + int(Freq_cal[i]) == 2):
                Req_List.update({SKUs[i]: 'B'})
            elif (int(value_cal[i]) + int(Qty_cal[i]) + int(Freq_cal[i]) == 1):
                Req_List.update({SKUs[i]: 'C'})
            else:
                Req_List.update({SKUs[i]: 'Q'})

        CSV_File = pd.DataFrame(Req_List, index=['Segmentation']).transpose()
        CSV_File.index.name = 'SKU'
        CSV_File.to_csv('ABC_Segmentation_Results.csv', encoding='utf-8')


if __name__ == '__main__':
    File = input('Enter File Name with .csv: ')
    abc = ABC_Analysis(File)
    abc.calc_abc_orders()
