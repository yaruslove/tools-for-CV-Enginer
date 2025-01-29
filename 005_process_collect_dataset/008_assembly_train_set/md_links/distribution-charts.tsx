import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

// Данные из таблицы README.md для первого графика (неравномерное распределение)
const rawData = [
  {
    class: 'Класс 1',
    'ТК Декабрь': 1860,
    'ТК Май': 0,
    'TG до Oct': 1332,
    'Сосногорск': 5329,
    'Лоток 21': 1625,
    'Лоток 19': 2809,
    'Sony Alex': 2958,
    'Листья Ольга': 640
  },
  {
    class: 'Класс 2',
    'ТК Декабрь': 2439,
    'ТК Май': 109,
    'TG до Oct': 4235,
    'Сосногорск': 6168,
    'Лоток 21': 3819,
    'Лоток 19': 1373,
    'Sony Alex': 1862,
    'Листья Ольга': 167
  },
  {
    class: 'Класс 3',
    'ТК Декабрь': 1481,
    'ТК Май': 317,
    'TG до Oct': 4744,
    'Сосногорск': 6087,
    'Лоток 21': 1060,
    'Лоток 19': 547,
    'Sony Alex': 1574,
    'Листья Ольга': 180
  },
  {
    class: 'Класс 4',
    'ТК Декабрь': 222,
    'ТК Май': 40,
    'TG до Oct': 935,
    'Сосногорск': 808,
    'Лоток 21': 146,
    'Лоток 19': 26,
    'Sony Alex': 243,
    'Листья Ольга': 7
  },
  {
    class: 'Класс 5',
    'ТК Декабрь': 34,
    'ТК Май': 0,
    'TG до Oct': 128,
    'Сосногорск': 141,
    'Лоток 21': 0,
    'Лоток 19': 0,
    'Sony Alex': 97,
    'Листья Ольга': 0
  },
  {
    class: 'Класс 6',
    'ТК Декабрь': 107,
    'ТК Май': 57,
    'TG до Oct': 46,
    'Сосногорск': 1699,
    'Лоток 21': 464,
    'Лоток 19': 154,
    'Sony Alex': 458,
    'Листья Ольга': 39
  },
  {
    class: 'Класс 7',
    'ТК Декабрь': 194,
    'ТК Май': 2,
    'TG до Oct': 90,
    'Сосногорск': 891,
    'Лоток 21': 84,
    'Лоток 19': 51,
    'Sony Alex': 884,
    'Листья Ольга': 11
  }
];

// Данные после балансировки (5000 изображений в каждом классе)
const balancedData = [
  { class: 'Класс 1', amount: 5000 },
  { class: 'Класс 2', amount: 5000 },
  { class: 'Класс 3', amount: 5000 },
  { class: 'Класс 4', amount: 5000 },
  { class: 'Класс 5', amount: 5000 },
  { class: 'Класс 6', amount: 5000 },
  { class: 'Класс 7', amount: 5000 }
];

const colors = [
  '#8884d8', '#82ca9d', '#ffc658', '#ff7300', '#a4de6c', '#d0ed57', '#83a6ed', '#8dd1e1'
];

export default function DistributionCharts() {
  return (
    <div className="w-full space-y-8">
      <div className="w-full h-96">
        <h3 className="text-lg font-semibold mb-4">Исходное распределение данных по классам и источникам</h3>
        <ResponsiveContainer>
          <BarChart data={rawData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="class" />
            <YAxis />
            <Tooltip />
            <Legend />
            {Object.keys(rawData[0])
              .filter(key => key !== 'class')
              .map((key, index) => (
                <Bar key={key} dataKey={key} fill={colors[index % colors.length]} stackId="a" />
              ))}
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="w-full h-96">
        <h3 className="text-lg font-semibold mb-4">Распределение после балансировки (5000 изображений в классе)</h3>
        <ResponsiveContainer>
          <BarChart data={balancedData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="class" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="amount" fill="#8884d8" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
