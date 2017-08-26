import pandas as pd
import math
import argparse


class DemandFilter():
    def __init__(self, datafile, savefile, orderlevel):
        self.datafile = datafile
        self.savefile = savefile
        self.orderlevel = orderlevel

    def demandfilter(self):
        file = pd.ExcelFile(self.datafile)
        df = file.parse('Sheet1')
        df = df[['Material','Ord. Qty.']]
        df = df[df['Ord. Qty.']>0]

        used_material_list = pd.DataFrame(pd.Series(df['Material']).value_counts())
        used_material_list = used_material_list[used_material_list['Material'] > 9] # No materials less than 9 lines
        all_materials = used_material_list.index.tolist()
        # all_materials = list(set(df['Material'].tolist()))
        datalist = []
        for material in all_materials:
             # 95% orders have to be manufactured
            sub_df = df[df['Material']== material]
            sub_df = sub_df.sort_values('Ord. Qty.')
            calc_table = pd.Series(sub_df['Ord. Qty.'])
            calc_table = calc_table.value_counts()
            calc_table = pd.DataFrame(calc_table)
            calc_table.index.name = 'Qty'
            calc_table = calc_table.sort_index()
            calc_table['Qty'] = calc_table.index
            calc_table['Sum'] =  calc_table['Qty']* calc_table['Ord. Qty.']
            calc_table['Weights'] = calc_table['Ord. Qty.']/calc_table['Ord. Qty.'].sum()
            calc_table['cum_sum'] = calc_table['Weights'].cumsum()
            calc_table['orders_count'] = calc_table['cum_sum'] <= self.orderlevel
            # total_order_qty = calc_table.loc(calc_table['orders_count'] == True, 'Sum').sum()

            try:
                total_order_qty = calc_table.groupby('orders_count')['Sum'].sum()[1]
                datalist.append([material, total_order_qty, self.orderlevel*100])
            except:
                total_order_qty = sum(calc_table['Sum'].tolist())
                datalist.append([material, math.ceil(total_order_qty*self.orderlevel), self.orderlevel*100])

        res = pd.DataFrame(datalist, columns=['Material Code', 'Qty', '% orders covered'])
        res.to_csv(self.savefile, encoding = 'utf-8', index = False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-level', default=0.95)
    parser.add_argument('-datafile', default='orders.xlsx')
    parser.add_argument('-savefile')
    args = parser.parse_args()
    orders_achiement_level = float(args.level)
    path = str(args.datafile)
    savefile = str(args.savefile)

    demand = DemandFilter(path, savefile, orders_achiement_level)
    demand.demandfilter()